#include "World/RVWorldContentLibrary.h"
#include "World/RVScavengeContainer.h"
#include "World/RVRegionStateSubsystem.h"
#include "World/RVEncounterDirector.h"
#include "World/RVRegionEncounterZone.h"
#include "Combat/RVInfected.h"
#include "Combat/RVInfectedProfile.h"
#include "Engine/DamageEvents.h"
#include "Inventory/RVWorldItem.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "WorldPartition/WorldPartition.h"
#include "PCGGraph.h"
#include "PCGNode.h"
#include "PCGComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "EngineUtils.h"
#include "Elements/PCGTypedGetter.h"
#include "Elements/PCGSurfaceSampler.h"
#include "Elements/PCGTransformPoints.h"
#include "Elements/PCGStaticMeshSpawner.h"
#include "MeshSelectors/PCGMeshSelectorWeighted.h"
#if WITH_EDITOR
#include "Landscape.h"
#include "LandscapeInfo.h"
#include "LandscapeStreamingProxy.h"
#include "LandscapeSubsystem.h"
#include "LandscapeEdit.h"
#include "LandscapeComponent.h"
#include "LandscapeEditLayer.h"
#include "LandscapeDataAccess.h"
#include "LandscapeSplinesComponent.h"
#include "Components/SplineMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "World/RVRegionRoad.h"
#include "WorldPartition/LoaderAdapter/LoaderAdapterShape.h"
#include "AssetRegistry/AssetRegistryModule.h"
#endif

AActor* URVWorldContentLibrary::CreateRegionLandscape(UObject* Context,int32 Components,float Spacing)
{
#if WITH_EDITOR
    UWorld* World=Context?Context->GetWorld():nullptr;
    if(!World || World->IsGameWorld() || Components<1 || Components>32 || !FMath::IsFinite(Spacing) || Spacing<100 || Spacing>1000) return nullptr;
    const int32 Quads=63,Size=Components*Quads+1;
    auto* Landscape=World->SpawnActor<ALandscape>();
    Landscape->SetActorLabel(TEXT("WNY rolling terrain"));
    Landscape->SetActorScale3D(FVector(Spacing,Spacing,100));
    Landscape->SetActorLocation(FVector(-.5*(Size-1)*Spacing,-.5*(Size-1)*Spacing,0));
    TArray<uint16> Heights;Heights.SetNumUninitialized(Size*Size);
    for(int32 Y=0;Y<Size;++Y)for(int32 X=0;X<Size;++X)
    {
        const double WX=(X-.5*(Size-1))*Spacing,WY=(Y-.5*(Size-1))*Spacing;
        // Gentle broad hills, with a central corridor flattened for the first authored roads.
        const double Hills=1800*FMath::Sin(WX/65000)*FMath::Cos(WY/72000)+650*FMath::Sin(WY/25000);
        const double RoadBlend=FMath::Clamp((FMath::Abs(WY)-3000)/12000,0.,1.);
        const double Height=Hills*RoadBlend;
        Heights[Y*Size+X]=uint16(FMath::Clamp(32768.+Height*128./100.,0.,65535.));
    }
    TMap<FGuid,TArray<uint16>> HeightMap;HeightMap.Add(FGuid(),MoveTemp(Heights));
    TMap<FGuid,TArray<FLandscapeImportLayerInfo>> Layers;Layers.Add(FGuid(),{});
    Landscape->Import(FGuid::NewGuid(),0,0,Size-1,Size-1,1,Quads,HeightMap,nullptr,Layers,
        ELandscapeImportAlphamapType::Additive,TArrayView<const FLandscapeLayer>());
    Landscape->CreateLandscapeInfo();Landscape->MarkPackageDirty();return Landscape;
#else
    return nullptr;
#endif
}
TMap<FString,bool> URVWorldContentLibrary::ValidateLootLifecycle(UObject* Context,URVLootProfile* Profile)
{
    TMap<FString,bool> Results;
#if !UE_BUILD_SHIPPING
    UWorld* World=Context?Context->GetWorld():nullptr;
    if(!World || !World->IsGameWorld() || World->GetNetMode()==NM_Client || !Profile) return Results;
    const FGuid Id=FGuid::NewGuid();
    auto Spawn=[&]()
    {
        auto* Actor=World->SpawnActorDeferred<ARVScavengeContainer>(ARVScavengeContainer::StaticClass(),FTransform(FVector(0,0,-10000)));
        Actor->ContainerId=Id;Actor->LootProfile=Profile;Actor->FinishSpawning(Actor->GetActorTransform());return Actor;
    };
    auto* First=Spawn();const auto Initial=First->Container->GetItems();
    Results.Add(TEXT("Profile produced supplies"),Initial.Num()>0);
    auto* Duplicate=Spawn();Results.Add(TEXT("Duplicate authored identity refuses generation"),Duplicate->Container->GetItems().IsEmpty());Duplicate->Destroy();
    auto* Receiver=World->SpawnActor<ARVStoragePoint>(FVector(0,0,-12000),FRotator::ZeroRotator);
    FString Error;bool Transferred=false,SecondRejected=false;
    if(!Initial.IsEmpty())
    {
        Transferred=First->Container->TransferAuthority(Receiver->Container,Initial[0].Id,Initial[0].Quantity,Error);
        SecondRejected=!First->Container->TransferAuthority(Receiver->Container,Initial[0].Id,Initial[0].Quantity,Error);
    }
    Results.Add(TEXT("Existing transaction transfers once"),Transferred && SecondRejected);
    const auto Remaining=First->Container->GetItems();First->Destroy();
    auto* Reloaded=Spawn();const auto Restored=Reloaded->Container->GetItems();
    bool Same=Restored.Num()==Remaining.Num();
    for(const auto& Item:Remaining)
        Same &= Restored.ContainsByPredicate([&](const auto& R){return R.Id==Item.Id && R.Quantity==Item.Quantity && R.Condition==Item.Condition;});
    Results.Add(TEXT("Unload recreation preserves remaining GUID quantity condition"),Same);
    Results.Add(TEXT("Transferred item does not respawn"),Initial.IsEmpty() || !Restored.ContainsByPredicate([&](const auto& R){return R.Id==Initial[0].Id;}));
    Reloaded->Destroy();Receiver->Destroy();World->GetSubsystem<URVRegionStateSubsystem>()->Containers.Remove(Id);
#endif
    return Results;
}

TMap<FString,FString> URVWorldContentLibrary::ValidateEncounterBookkeeping(UObject* Context)
{
    TMap<FString,FString> R;
#if !UE_BUILD_SHIPPING
    UWorld* World=Context?Context->GetWorld():nullptr;
    if(!World || !World->IsGameWorld() || World->GetNetMode()==NM_Client)return R;
    auto* Director=World->GetSubsystem<URVEncounterDirector>();auto* State=World->GetSubsystem<URVRegionStateSubsystem>();
    const ARVRegionEncounterZone* Authored=nullptr;
    for(TActorIterator<ARVRegionEncounterZone> It(World);It;++It)if(It->Profile && It->Profile->InfectedProfile && It->Profile->SupplyProfile && It->SupplyCacheClass){Authored=*It;break;}
    if(!Director || !State || !Authored){R.Add(TEXT("Setup"),TEXT("false: needs region director and an authored zone with infected/supply profiles"));return R;}
    auto Pass=[&](const TCHAR* Name,bool Ok,const FString& Detail){R.Add(Name,FString::Printf(TEXT("%s: %s"),Ok?TEXT("true"):TEXT("false"),*Detail));};
    // Preserve the live session pacing; every record added below is removed again.
    const double SavedNext=Director->NextEventTime;const TArray<ERVEncounterOutcome> SavedRecent=Director->Recent;
    auto* Profile=NewObject<URVEncounterProfile>(GetTransientPackage());
    Profile->InfectedProfile=Authored->Profile->InfectedProfile;Profile->SupplyProfile=Authored->Profile->SupplyProfile;Profile->EventCooldown=150;
    {FRVEncounterChoice Quiet;Quiet.Outcome=ERVEncounterOutcome::Quiet;Quiet.Weight=.01f;FRVEncounterChoice Cluster;Cluster.Outcome=ERVEncounterOutcome::InfectedCluster;Cluster.Weight=100.f;Cluster.InfectedCount=2;Profile->Choices={Quiet,Cluster};}
    const TArray<FVector> Positions={FVector(0,0,-30000),FVector(300,0,-30000)};
    TArray<FGuid> TestIds;FGuid Cluster;
    for(int32 Attempt=0;Attempt<32 && !Cluster.IsValid();++Attempt)
    {
        const FGuid Id=FGuid::NewGuid();TestIds.Add(Id);Director->NextEventTime=0;Director->Recent.Reset();
        if(Director->SelectAuthority(Id,Profile,Positions).Outcome==ERVEncounterOutcome::InfectedCluster)Cluster=Id;
    }
    const double Now=World->GetTimeSeconds();
    Pass(TEXT("Non-quiet selection starts the global cooldown"),Cluster.IsValid() && FMath::IsNearlyEqual(Director->NextEventTime,Now+150,0.5),FString::Printf(TEXT("next=%.2f now=%.2f"),Director->NextEventTime,Now));
    const FGuid During=FGuid::NewGuid();TestIds.Add(During);
    {const FRVEncounterSnapshot Cooled=Director->SelectAuthority(During,Profile,Positions);
     Pass(TEXT("Zone evaluated during cooldown stays quiet with no population"),Cooled.bSelected && Cooled.Outcome==ERVEncounterOutcome::Quiet && Cooled.Infected.IsEmpty(),TEXT("cooldown blocks a second non-quiet outcome"));}
    Director->NextEventTime=0;
    {const FRVEncounterSnapshot Again=Director->SelectAuthority(During,Profile,Positions);const FRVEncounterSnapshot First=Director->SelectAuthority(Cluster,Profile,Positions);
     Pass(TEXT("Selected outcomes stay stable for the session"),Again.Outcome==ERVEncounterOutcome::Quiet && First.Outcome==ERVEncounterOutcome::InfectedCluster,TEXT("re-selection after cooldown does not reroll"));}
    auto* NoQuiet=NewObject<URVEncounterProfile>(GetTransientPackage());
    {FRVEncounterChoice Only;Only.Outcome=ERVEncounterOutcome::InfectedCluster;Only.Weight=1.f;NoQuiet->Choices={Only};}
    const FGuid Unsafe=FGuid::NewGuid();TestIds.Add(Unsafe);Director->NextEventTime=0;
    Pass(TEXT("Profile without weighted quiet travel falls back to quiet"),Director->SelectAuthority(Unsafe,NoQuiet,Positions).Outcome==ERVEncounterOutcome::Quiet,TEXT("guard against constant action"));
    // Dead/suspended member bookkeeping through the real zone suspend path, far below the playable terrain.
    auto* Zone=World->SpawnActorDeferred<ARVRegionEncounterZone>(ARVRegionEncounterZone::StaticClass(),FTransform(FVector(0,0,-30000)));
    Zone->ZoneId=Cluster;Zone->Profile=Profile;Zone->SupplyCacheClass=Authored->SupplyCacheClass;Zone->FinishSpawning(FTransform(FVector(0,0,-30000)));
    auto Spawn=[&](const FVector& At)
    {
        auto* I=World->SpawnActorDeferred<ARVInfected>(ARVInfected::StaticClass(),FTransform(At),nullptr,nullptr,ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
        I->Profile=Profile->InfectedProfile;I->FinishSpawning(FTransform(At));
        I->GetCharacterMovement()->DisableMovement();I->GetCharacterMovement()->GravityScale=0;Director->ActiveInfected.Add(I);return I;
    };
    FRVEncounterSnapshot* Record=Director->Encounters.Find(Cluster);
    if(Record && Record->Infected.Num()==2 && Zone->bOwnsIdentity)
    {
        auto* Killed=Spawn(FVector(0,0,-30000));auto* Hurt=Spawn(FVector(400,0,-30000));
        Zone->Members.Add(0,Killed);Zone->Members.Add(1,Hurt);Zone->bActive=true;
        Killed->TakeDamage(100000,FDamageEvent(),nullptr,nullptr);Hurt->TakeDamage(10,FDamageEvent(),nullptr,nullptr);
        const float HurtVitality=Hurt->Vitality;const FVector HurtAt=Hurt->GetActorLocation();const bool KilledDead=Killed->State==ERVInfectedState::Dead;
        Zone->SuspendAuthority();Record=Director->Encounters.Find(Cluster);
        Pass(TEXT("Killed member is recorded dead on suspend"),KilledDead && Record->Infected[0].bDead,TEXT("normal TakeDamage death"));
        Pass(TEXT("Living member keeps vitality and position on suspend"),!Record->Infected[1].bDead && FMath::IsNearlyEqual(Record->Infected[1].Vitality,HurtVitality) && Record->Infected[1].Position.Equals(HurtAt,1),FString::Printf(TEXT("vitality=%.2f of %.2f"),Record->Infected[1].Vitality,Profile->InfectedProfile?Profile->InfectedProfile->Vitality:0.f));
        Pass(TEXT("Suspend releases member actors"),(!IsValid(Killed) || Killed->IsActorBeingDestroyed()) && (!IsValid(Hurt) || Hurt->IsActorBeingDestroyed()) && Zone->Members.IsEmpty(),TEXT("no retained actor"));
        auto* Lost=Spawn(FVector(800,0,-30000));Zone->Members.Add(1,Lost);Zone->bActive=true;Lost->Destroy();
        Zone->SuspendAuthority();Record=Director->Encounters.Find(Cluster);
        Pass(TEXT("Externally destroyed member is exhausted, never respawned"),Record->Infected[1].bDead,TEXT("missing actor at suspend"));
    }
    else Pass(TEXT("Cluster record prepared"),false,FString::Printf(TEXT("record=%d owns=%d"),Record!=nullptr,Zone->bOwnsIdentity));
    // Supply cache: the zone's cache uses a stable derived GUID, so revisits restore only what remains.
    const FGuid CacheId(Cluster.A^0xA70C164D,Cluster.B,Cluster.C,Cluster.D);
    auto SpawnCache=[&]()
    {
        auto* C=World->SpawnActorDeferred<ARVScavengeContainer>(Authored->SupplyCacheClass,FTransform(FVector(0,800,-30000)),nullptr,nullptr,ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
        C->ContainerId=CacheId;C->LootProfile=Profile->SupplyProfile;C->FinishSpawning(C->GetActorTransform());return C;
    };
    auto* First=SpawnCache();Zone->Cache=First;Zone->bActive=true;const auto Initial=First->Container->GetItems();
    auto* Receiver=World->SpawnActor<ARVStoragePoint>(FVector(0,1600,-30000),FRotator::ZeroRotator);FString Error;bool Moved=false;
    if(!Initial.IsEmpty())Moved=First->Container->TransferAuthority(Receiver->Container,Initial[0].Id,Initial[0].Quantity,Error);
    const auto Remaining=First->Container->GetItems();
    Zone->SuspendAuthority();
    Pass(TEXT("Suspend destroys the cache actor"),!IsValid(First) || First->IsActorBeingDestroyed(),TEXT("cache released with the zone"));
    auto* Revisit=SpawnCache();const auto Restored=Revisit->Container->GetItems();bool Same=Restored.Num()==Remaining.Num();
    for(const auto& Item:Remaining)Same&=Restored.ContainsByPredicate([&](const auto& X){return X.Id==Item.Id && X.Quantity==Item.Quantity && X.Condition==Item.Condition;});
    Pass(TEXT("Cache revisit restores remaining GUID/quantity/condition"),!Initial.IsEmpty() && Moved && Same,FString::Printf(TEXT("initial=%d remaining=%d restored=%d"),Initial.Num(),Remaining.Num(),Restored.Num()));
    Pass(TEXT("Taken cache item does not respawn"),!Initial.IsEmpty() && !Restored.ContainsByPredicate([&](const auto& X){return X.Id==Initial[0].Id;}),TEXT("searched/taken state kept"));
    Revisit->Destroy();Receiver->Destroy();Zone->Destroy();
    for(const FGuid& Id:TestIds)Director->Encounters.Remove(Id);
    State->Containers.Remove(CacheId);State->ActiveContainers.Remove(CacheId);
    Director->NextEventTime=SavedNext;Director->Recent=SavedRecent;
    Pass(TEXT("Transient records removed and session pacing restored"),!Director->Encounters.Contains(Cluster) && Director->NextEventTime==SavedNext,FString::Printf(TEXT("records=%d"),Director->Encounters.Num()));
#endif
    return R;
}

UPCGGraph* URVWorldContentLibrary::CreateBiomeGraph(const FString& Path,const TArray<UStaticMesh*>& Meshes,float Density,bool Collision)
{
#if WITH_EDITOR
    if(Meshes.IsEmpty() || !Path.StartsWith(TEXT("/Game/World/WNY/")) || !FMath::IsFinite(Density) || Density<=0 || Density>.1f)return nullptr;
    if(auto* Existing=LoadObject<UPCGGraph>(nullptr,*(Path+TEXT(".")+FPackageName::GetLongPackageAssetName(Path))))return Existing;
    auto* Package=CreatePackage(*Path);
    auto* Graph=NewObject<UPCGGraph>(Package,*FPackageName::GetLongPackageAssetName(Path),RF_Public|RF_Standalone|RF_Transactional);
    UPCGGetLandscapeSettings* Landscape=nullptr;auto* Get=Graph->AddNodeOfType(Landscape);
    Landscape->bUnbounded=false;
    UPCGSurfaceSamplerSettings* Sampler=nullptr;auto* Sample=Graph->AddNodeOfType(Sampler);
    Sampler->PointsPerSquaredMeter=Density;Sampler->PointExtents=FVector(150);Sampler->bUnbounded=false;
    UPCGTransformPointsSettings* Transform=nullptr;auto* Rotate=Graph->AddNodeOfType(Transform);
    Transform->bAbsoluteRotation=true;Transform->RotationMax=FRotator(0,360,0);
    Transform->ScaleMin=FVector(.8);Transform->ScaleMax=FVector(1.2);Transform->bUniformScale=true;
    UPCGStaticMeshSpawnerSettings* Spawner=nullptr;auto* Spawn=Graph->AddNodeOfType(Spawner);
    Spawner->SetMeshSelectorType(UPCGMeshSelectorWeighted::StaticClass());
    auto* Selector=CastChecked<UPCGMeshSelectorWeighted>(Spawner->MeshSelectorParameters);
    for(auto* Mesh:Meshes)if(Mesh)
    {
        FPCGMeshSelectorWeightedEntry Entry(Mesh,1);
        Entry.Descriptor.BodyInstance.SetCollisionProfileName(Collision?TEXT("BlockAll"):TEXT("NoCollision"));
        Selector->MeshEntries.Add(Entry);
    }
    Graph->AddEdge(Get,TEXT("Out"),Sample,TEXT("Surface"));
    Graph->AddEdge(Sample,TEXT("Out"),Rotate,TEXT("In"));
    Graph->AddEdge(Rotate,TEXT("Out"),Spawn,TEXT("In"));
    Graph->AddEdge(Spawn,TEXT("Out"),Graph->GetOutputNode(),TEXT("Out"));
    FAssetRegistryModule::AssetCreated(Graph);Graph->MarkPackageDirty();return Graph;
#else
    return nullptr;
#endif
}
TMap<FString,int32> URVWorldContentLibrary::GetDressingStats(UObject* Context)
{
    TMap<FString,int32> Result;Result.Add(TEXT("Pending"),0);Result.Add(TEXT("Instances"),0);Result.Add(TEXT("OtherInstances"),0);Result.Add(TEXT("Components"),0);
    if(auto* World=Context?Context->GetWorld():nullptr)
        for(TActorIterator<AActor> It(World);It;++It)
        {
            TArray<UPCGComponent*> PCG;It->GetComponents(PCG);
            for(auto* C:PCG){++Result[TEXT("Components")];if(C->IsGenerating())++Result[TEXT("Pending")];}
            TArray<UInstancedStaticMeshComponent*> Instances;It->GetComponents(Instances);
            // Distant HLOD copies are not additional source PCG foliage.
            for(auto* C:Instances)Result[PCG.Num()>0?TEXT("Instances"):TEXT("OtherInstances")]+=C->GetInstanceCount();
        }
    return Result;
}

bool URVWorldContentLibrary::ConfigureRegionStreaming(UObject* Context)
{
#if WITH_EDITOR
    auto* World=Context?Context->GetWorld():nullptr;
    if(!World || World->IsGameWorld() || World->GetPackage()->GetName()!=TEXT("/Game/Maps/WNY_PrototypeRegion")) return false;
    auto* Partition=World->GetWorldPartition();if(!Partition) return false;
    Partition->Modify();Partition->SetEnableStreaming(true);
    Partition->ServerStreamingMode=EWorldPartitionServerStreamingMode::Enabled;
    Partition->ServerStreamingOutMode=EWorldPartitionServerStreamingOutMode::Enabled;
    World->MarkPackageDirty();return true;
#else
    return false;
#endif
}
TMap<FString,FString> URVWorldContentLibrary::InspectRegion(UObject* Context)
{
    TMap<FString,FString> Result;
    auto* World=Context?Context->GetWorld():nullptr;if(!World)return Result;
    if(auto* Partition=World->GetWorldPartition())
    {
        Result.Add(TEXT("Streaming enabled"),Partition->IsStreamingEnabled()?TEXT("true"):TEXT("false"));
        Result.Add(TEXT("Server streaming mode"),FString::FromInt(int32(Partition->ServerStreamingMode)));
        Result.Add(TEXT("Server streaming out mode"),FString::FromInt(int32(Partition->ServerStreamingOutMode)));
    }
    for(TActorIterator<AActor> It(World);It;++It)
    {
        TArray<UPCGComponent*> Components;It->GetComponents(Components);
        for(auto* C:Components)
        {
            const FString Key=It->GetName()+TEXT("/")+C->GetName();
            Result.Add(Key,FString::Printf(TEXT("Graph=%s;Generating=%d;Partitioned=%d"),
                *GetNameSafe(C->GetGraph()),C->IsGenerating(),C->bIsComponentPartitioned));
        }
        TArray<UInstancedStaticMeshComponent*> Instances;It->GetComponents(Instances);
        for(auto* C:Instances)
            Result.Add(It->GetName()+TEXT("/")+C->GetName(),FString::Printf(TEXT("Mesh=%s;Instances=%d"),
                *GetNameSafe(C->GetStaticMesh()),C->GetInstanceCount()));
    }
    return Result;
}
bool URVWorldContentLibrary::SetRegionAuthoringLoaded(UObject* Context,bool Loaded)
{
#if WITH_EDITOR
    auto* World=Context?Context->GetWorld():nullptr;
    if(!World || World->IsGameWorld() || World->GetPackage()->GetName()!=TEXT("/Game/Maps/WNY_PrototypeRegion")) return false;
    auto* Partition=World->GetWorldPartition();if(!Partition) return false;
    const FString Label(TEXT("WNY authoring audit"));
    for(const auto& Adapter:Partition->GetRegisteredEditorLoaderAdapters())
        if(Adapter && Adapter->GetLoaderAdapter() && Adapter->GetLoaderAdapter()->GetLabel()==Label)
        {
            if(!Loaded)Partition->ReleaseEditorLoaderAdapter(Adapter);
            return true;
        }
    if(Loaded)
    {
        auto* Adapter=Partition->CreateEditorLoaderAdapter<FLoaderAdapterShape>(World,
            FBox(FVector(-205000,-205000,-30000),FVector(205000,205000,30000)),Label);
        Adapter->GetLoaderAdapter()->Load();
    }
    return true;
#else
    return false;
#endif
}

TMap<FString,int32> URVWorldContentLibrary::PartitionRegionLandscape(UObject* Context)
{
    TMap<FString,int32> Result;
#if WITH_EDITOR
    auto* World=Context?Context->GetWorld():nullptr;
    if(!World || World->IsGameWorld() || World->GetPackage()->GetName()!=TEXT("/Game/Maps/WNY_PrototypeRegion") || !World->GetWorldPartition())return Result;
    ALandscape* Terrain=nullptr;int32 Parents=0;
    for(TActorIterator<ALandscape> It(World);It;++It){Terrain=*It;++Parents;}
    Result.Add(TEXT("Landscape parents"),Parents);
    if(Parents!=1 || !Terrain || !Terrain->GetLandscapeInfo())return Result;
    int32 Proxies=0;
    for(TActorIterator<ALandscapeStreamingProxy> It(World);It;++It)if(It->GetLandscapeActor()==Terrain)++Proxies;
    if(Proxies==0)
    {
        // This supported engine path converts non-grid terrain, not an arbitrary
        // regrid of previously authored landscapes. Never touch accepted maps.
        if(auto* Subsystem=World->GetSubsystem<ULandscapeSubsystem>())
        {
            Terrain->Modify();Subsystem->ChangeGridSize(Terrain->GetLandscapeInfo(),2);
            Terrain->MarkPackageDirty();
        }
    }
    Proxies=0;int32 Components=Terrain->LandscapeComponents.Num();
    for(TActorIterator<ALandscapeStreamingProxy> It(World);It;++It)
        if(It->GetLandscapeActor()==Terrain){++Proxies;Components+=It->LandscapeComponents.Num();It->MarkPackageDirty();}
    Result.Add(TEXT("Streaming proxies"),Proxies);Result.Add(TEXT("Terrain components"),Components);
#endif
    return Result;
}

TMap<FString,int32> URVWorldContentLibrary::GradeRegionSitePads(UObject* Context,bool bExtendGarage)
{
    TMap<FString,int32> Result;
#if WITH_EDITOR
    UWorld* World=Context?Context->GetWorld():nullptr;
    if(!World || World->IsGameWorld() || !World->GetPackage()->GetName().EndsWith(TEXT("/WNY_PrototypeRegion")))return Result;
    // V3 grades the sites and the garage extension together; the separate V2-only pass is superseded.
    if(bExtendGarage)return Result;
    ALandscape* Landscape=nullptr;
    for(TActorIterator<ALandscape> It(World);It;++It){if(Landscape)return Result;Landscape=*It;}
    // V1/V2 tags were saved although their final-heightmap writes were discarded by the edit layer merge.
    const FName Marker=TEXT("WNYGradedSitesV3");
    if(!Landscape || Landscape->ActorHasTag(Marker))return Result;
    auto* Info=Landscape->GetLandscapeInfo();int32 MinX,MinY,MaxX,MaxY;
    if(!Info || !Info->GetLandscapeExtent(MinX,MinY,MaxX,MaxY) || MaxX-MinX>2048 || MaxY-MinY>2048)return Result;
    const TArray<const ULandscapeEditLayerBase*> Layers=Landscape->GetEditLayersConst();
    if(Layers.Num()!=1 || !Layers[0] || Layers[0]->IsLocked())return Result;
    const auto OriginalHeight=[](double X,double Y)
    {return (1800*FMath::Sin(X/65000)*FMath::Cos(Y/72000)+650*FMath::Sin(Y/25000))*FMath::Clamp((FMath::Abs(Y)-3000)/12000,0.,1.);};
    struct FSite{FVector2D Center,Half;double Height;};
    TArray<FSite> Sites={{{-130000,4900},{2500,2900},0},{{-60000,-5500},{3000,4100},0},
        {{0,46000},{2800,3500},OriginalHeight(0,45000)},{{75000,46000},{2800,3500},OriginalHeight(75000,45000)},
        {{140000,5000},{2500,3900},0}};
    // One 400 cm Landscape quad beyond each authored pad keeps the pad edge flat instead of interpolating into the falloff.
    for(FSite& Site:Sites)Site.Half+=FVector2D(400,400);
    const TArray<FSite> Garage={{{-60000,-7000},{4000,6600},0}};
    const TPair<const TArray<FSite>*,double> Passes[]={{&Sites,1400.},{&Garage,9000.}};
    for(TActorIterator<ALandscapeProxy> It(World);It;++It)
    {It->Modify();for(const auto& Component:It->LandscapeComponents)if(Component)Component->Modify();}
    const int32 Width=MaxX-MinX+1;TArray<uint16> Heights;Heights.SetNumUninitialized(Width*(MaxY-MinY+1));int32 Changed=0;
    {
        // Read and write the persistent edit layer itself; the final heightmap is regenerated from it.
        FScopedSetLandscapeEditingLayer Scope(Landscape,Layers[0]->GetGuid());
        FLandscapeEditDataInterface Edit(Info);Edit.GetHeightDataFast(MinX,MinY,MaxX,MaxY,Heights.GetData(),Width);
        for(const uint16 Height:Heights)if(Height<28000 || Height>38000)return Result; // Refuse unloaded/missing terrain samples.
        for(int32 Y=MinY;Y<=MaxY;++Y)for(int32 X=MinX;X<=MaxX;++X)
        {
            const FVector P=Landscape->GetActorTransform().TransformPosition(FVector(X,Y,0));
            const int32 Index=(Y-MinY)*Width+X-MinX;double Height=(int32(Heights[Index])-32768)*100./128.;
            for(const auto& Pass:Passes)for(const auto& Site:*Pass.Key)
            {
                const double Outside=FMath::Max(FMath::Abs(P.X-Site.Center.X)-Site.Half.X,FMath::Abs(P.Y-Site.Center.Y)-Site.Half.Y);
                const double Alpha=FMath::SmoothStep(0.,1.,FMath::Clamp(1.-FMath::Max(0.,Outside)/Pass.Value,0.,1.));
                Height=FMath::Lerp(Height,Site.Height,Alpha);
            }
            const uint16 Value=uint16(FMath::Clamp(FMath::RoundToInt(32768.+Height*128./100.),0,65535));
            if(Value!=Heights[Index]){Heights[Index]=Value;++Changed;}
        }
        Edit.SetHeightData(MinX,MinY,MaxX,MaxY,Heights.GetData(),Width,true);Edit.Flush();
    }
    // Merge the edited layer into the final heightmap, normals and collision now, not on a later tick.
    Landscape->RequestLayersContentUpdateForceAll(ELandscapeLayerUpdateMode::Update_All);Landscape->ForceUpdateLayersContent();
    Landscape->Tags.Add(Marker);Landscape->MarkPackageDirty();
    for(TActorIterator<ALandscapeProxy> It(World);It;++It)It->MarkPackageDirty();
    Result.Add(TEXT("ChangedVertices"),Changed);Result.Add(TEXT("GradedSites"),Sites.Num()+Garage.Num());
#endif
    return Result;
}



TMap<FString,int32> URVWorldContentLibrary::BlendRegionTerrainToPavement(UObject* Context)
{
    TMap<FString,int32> Result;
#if WITH_EDITOR
    UWorld* World=Context?Context->GetWorld():nullptr;
    if(!World || World->IsGameWorld() || !World->GetPackage()->GetName().EndsWith(TEXT("/WNY_PrototypeRegion")))return Result;
    ALandscape* Landscape=nullptr;
    for(TActorIterator<ALandscape> It(World);It;++It){if(Landscape)return Result;Landscape=*It;}
    const FName Marker=TEXT("WNYPavedEdgesV1");
    if(!Landscape || Landscape->ActorHasTag(Marker) || !Landscape->ActorHasTag(TEXT("WNYGradedSitesV3")))return Result;
    auto* Info=Landscape->GetLandscapeInfo();int32 MinX,MinY,MaxX,MaxY;
    if(!Info || !Info->GetLandscapeExtent(MinX,MinY,MaxX,MaxY) || MaxX-MinX>2048 || MaxY-MinY>2048)return Result;
    const TArray<const ULandscapeEditLayerBase*> Layers=Landscape->GetEditLayersConst();
    if(Layers.Num()!=1 || !Layers[0] || Layers[0]->IsLocked())return Result;
    // Paved surfaces: every road spline mesh with collision and each site's "RV parking" slab.
    TArray<UPrimitiveComponent*> Paved;int32 Slabs=0;
    for(TActorIterator<AActor> It(World);It;++It)
    {
        if(Cast<ARVRegionRoad>(*It))
        {
            TArray<USplineMeshComponent*> Meshes;It->GetComponents(Meshes);
            for(auto* Mesh:Meshes)if(Mesh && Mesh->IsQueryCollisionEnabled())Paved.Add(Mesh);
        }
        else if(Cast<AStaticMeshActor>(*It) && It->GetActorLabel().EndsWith(TEXT(" RV parking")))
        {Paved.Add(CastChecked<AStaticMeshActor>(*It)->GetStaticMeshComponent());++Slabs;}
    }
    if(Paved.IsEmpty() || Slabs!=5)return Result;
    const double Bucket=2000;TMap<FIntPoint,TArray<int32>> Buckets;
    for(int32 Index=0;Index<Paved.Num();++Index)
    {
        const FBox Box=Paved[Index]->Bounds.GetBox();
        for(int32 BX=FMath::FloorToInt(Box.Min.X/Bucket);BX<=FMath::FloorToInt(Box.Max.X/Bucket);++BX)
            for(int32 BY=FMath::FloorToInt(Box.Min.Y/Bucket);BY<=FMath::FloorToInt(Box.Max.Y/Bucket);++BY)Buckets.FindOrAdd({BX,BY}).Add(Index);
    }
    const int32 Width=MaxX-MinX+1,Height=MaxY-MinY+1,Count=Width*Height;const FTransform Transform=Landscape->GetActorTransform();
    // Paved vertices sit 6 cm under the pavement top; the first ring meets the traced pavement edge 3 cm low; then a smooth 3-quad blend.
    constexpr double SurfaceOffset=-6,EdgeOffset=-3;constexpr int32 Blend=4;
    TArray<double> Source;Source.Init(TNumericLimits<double>::Lowest(),Count);TArray<int32> Distance;Distance.Init(MAX_int32,Count);TArray<int32> Queue;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RVPavementBlend),false); // Simple collision: what vehicles actually drive on.
    const auto TopAt=[&](double PX,double PY)
    {
        double Top=TNumericLimits<double>::Lowest();
        if(const TArray<int32>* Candidates=Buckets.Find(FIntPoint(int32(FMath::FloorToInt(PX/Bucket)),int32(FMath::FloorToInt(PY/Bucket)))))
            for(const int32 Candidate:*Candidates)
            {
                const FBox Box=Paved[Candidate]->Bounds.GetBox();
                if(PX<Box.Min.X || PX>Box.Max.X || PY<Box.Min.Y || PY>Box.Max.Y)continue;
                FHitResult Hit;
                if(Paved[Candidate]->LineTraceComponent(Hit,FVector(PX,PY,Box.Max.Z+100),FVector(PX,PY,Box.Min.Z-100),Params))Top=FMath::Max(Top,Hit.ImpactPoint.Z);
            }
        return Top;
    };
    for(int32 Y=MinY;Y<=MaxY;++Y)for(int32 X=MinX;X<=MaxX;++X)
    {
        const FVector P=Transform.TransformPosition(FVector(X,Y,0));const double Top=TopAt(P.X,P.Y);
        if(Top>TNumericLimits<double>::Lowest())
        {const int32 Index=(Y-MinY)*Width+X-MinX;Source[Index]=Top+SurfaceOffset;Distance[Index]=0;Queue.Add(Index);}
    }
    if(Queue.IsEmpty())return Result;
    const int32 PavedVertices=Queue.Num();
    // Ring by ring, each vertex takes the mean of its inner-ring neighbours, so slopes along a road cancel instead of copying one uphill/downhill neighbour.
    for(int32 Head=0;Head<Queue.Num();++Head)
    {
        const int32 Index=Queue[Head],X=Index%Width,Y=Index/Width;if(Distance[Index]>=Blend)continue;
        for(int32 DY=-1;DY<=1;++DY)for(int32 DX=-1;DX<=1;++DX)
        {
            const int32 NX=X+DX,NY=Y+DY;if(NX<0 || NY<0 || NX>=Width || NY>=Height)continue;
            const int32 Next=NY*Width+NX;if(Distance[Next]!=MAX_int32)continue;
            Distance[Next]=Distance[Index]+1;Queue.Add(Next);
            double Sum=0;int32 Inner=0;
            for(int32 EY=-1;EY<=1;++EY)for(int32 EX=-1;EX<=1;++EX)
            {
                const int32 MX=NX+EX,MY=NY+EY;if(MX<0 || MY<0 || MX>=Width || MY>=Height)continue;
                const int32 Neighbour=MY*Width+MX;if(Distance[Neighbour]==Distance[Next]-1){Sum+=Source[Neighbour];++Inner;}
            }
            Source[Next]=Sum/Inner;
            if(Distance[Next]==1)
            {
                // First ring: take the pavement edge height itself, found by stepping from this vertex toward each paved neighbour.
                const FVector P=Transform.TransformPosition(FVector(NX+MinX,NY+MinY,0));double EdgeSum=0;int32 Edges=0;
                for(int32 EY=-1;EY<=1;++EY)for(int32 EX=-1;EX<=1;++EX)
                {
                    const int32 MX=NX+EX,MY=NY+EY;if(MX<0 || MY<0 || MX>=Width || MY>=Height || Distance[MY*Width+MX]!=0)continue;
                    const FVector Q=Transform.TransformPosition(FVector(MX+MinX,MY+MinY,0));
                    for(double T=0.05;T<=1.;T+=0.05)
                        if(const double Top=TopAt(FMath::Lerp(P.X,Q.X,T),FMath::Lerp(P.Y,Q.Y,T));Top>TNumericLimits<double>::Lowest()){EdgeSum+=Top;++Edges;break;}
                }
                if(Edges)Source[Next]=EdgeSum/Edges+EdgeOffset;
            }
        }
    }
    for(TActorIterator<ALandscapeProxy> It(World);It;++It)
    {It->Modify();for(const auto& Component:It->LandscapeComponents)if(Component)Component->Modify();}
    TArray<uint16> Heights;Heights.SetNumUninitialized(Count);int32 Changed=0;double MaxRaise=0,MaxLower=0;
    {
        FScopedSetLandscapeEditingLayer Scope(Landscape,Layers[0]->GetGuid());
        FLandscapeEditDataInterface Edit(Info);Edit.GetHeightDataFast(MinX,MinY,MaxX,MaxY,Heights.GetData(),Width);
        for(const uint16 Value:Heights)if(Value<28000 || Value>38000)return Result; // Refuse unloaded/missing terrain samples.
        TArray<double> H;H.SetNumUninitialized(Count);for(int32 Index=0;Index<Count;++Index)H[Index]=(int32(Heights[Index])-32768)*100./128.;
        const TArray<double> Original=H;
        for(const int32 Index:Queue)
        {
            const double Alpha=Distance[Index]<=1?1.:FMath::SmoothStep(0.,1.,1.-double(Distance[Index]-1)/Blend);
            H[Index]=FMath::Lerp(H[Index],Source[Index],Alpha);
        }
        // Second smoothing pass: sample 16 points in every quad touching the pavement and nudge the corner vertices until the
        // interpolated terrain sits 6 cm under the pavement inside it and 3 cm under the nearest pavement edge within 1 m outside it.
        TSet<int32> Quads;
        for(const int32 Index:Queue)if(Distance[Index]<=1)
        {const int32 X=Index%Width,Y=Index/Width;for(int32 DY=-1;DY<=0;++DY)for(int32 DX=-1;DX<=0;++DX)if(X+DX>=0 && Y+DY>=0 && X+DX<Width-1 && Y+DY<Height-1)Quads.Add((Y+DY)*Width+X+DX);}
        struct FFine{int32 Quad;double U,V,Desired;};TArray<FFine> Fine;
        static const FVector2D Directions[]={{1,0},{-1,0},{0,1},{0,-1},{.7071,.7071},{.7071,-.7071},{-.7071,.7071},{-.7071,-.7071}};
        for(const int32 Quad:Quads)
        {
            const int32 X=Quad%Width,Y=Quad/Width;
            for(const double U:{.125,.375,.625,.875})for(const double V:{.125,.375,.625,.875})
            {
                const FVector P=Transform.TransformPosition(FVector(X+MinX+U,Y+MinY+V,0));const double Top=TopAt(P.X,P.Y);
                if(Top>TNumericLimits<double>::Lowest()){Fine.Add({Quad,U,V,Top-6});continue;}
                double Edge=TNumericLimits<double>::Lowest();
                for(const FVector2D& D:Directions)Edge=FMath::Max(Edge,TopAt(P.X+D.X*100,P.Y+D.Y*100));
                if(Edge>TNumericLimits<double>::Lowest())Fine.Add({Quad,U,V,Edge-3});
            }
        }
        TArray<double> Num,Den;
        for(int32 Iteration=0;Iteration<16;++Iteration)
        {
            Num.Init(0,Count);Den.Init(0,Count);
            for(const FFine& F:Fine)
            {
                // Same split as Chaos heightfield collision (diagonal from cell origin to its far corner).
                const int32 C[4]={F.Quad,F.Quad+1,F.Quad+Width,F.Quad+Width+1};
                const double W[4]={F.U<F.V?1-F.V:1-F.U,F.U<F.V?0:F.U-F.V,F.U<F.V?F.V-F.U:0,F.U<F.V?F.U:F.V};
                const double Error=F.Desired-(W[0]*H[C[0]]+W[1]*H[C[1]]+W[2]*H[C[2]]+W[3]*H[C[3]]);
                for(int32 K=0;K<4;++K){Num[C[K]]+=W[K]*Error;Den[C[K]]+=W[K];}
            }
            for(const int32 Index:Queue)if(Den[Index]>0 && Distance[Index]<=3)H[Index]+=FMath::Clamp(Num[Index]/Den[Index],-30.,30.);
        }
        for(const int32 Index:Queue)
        {
            const uint16 Value=uint16(FMath::Clamp(FMath::RoundToInt(32768.+H[Index]*128./100.),0,65535));
            if(Value!=Heights[Index]){MaxRaise=FMath::Max(MaxRaise,H[Index]-Original[Index]);MaxLower=FMath::Min(MaxLower,H[Index]-Original[Index]);Heights[Index]=Value;++Changed;}
        }
        Result.Add(TEXT("SmoothingSamples"),Fine.Num());Result.Add(TEXT("SmoothingQuads"),Quads.Num());
        Edit.SetHeightData(MinX,MinY,MaxX,MaxY,Heights.GetData(),Width,true);Edit.Flush();
    }
    Landscape->RequestLayersContentUpdateForceAll(ELandscapeLayerUpdateMode::Update_All);Landscape->ForceUpdateLayersContent();
    Landscape->Tags.Add(Marker);Landscape->MarkPackageDirty();
    for(TActorIterator<ALandscapeProxy> It(World);It;++It)It->MarkPackageDirty();
    Result.Add(TEXT("PavedComponents"),Paved.Num());Result.Add(TEXT("ParkingSlabs"),Slabs);Result.Add(TEXT("PavedVertices"),PavedVertices);
    Result.Add(TEXT("BlendedVertices"),Queue.Num());Result.Add(TEXT("ChangedVertices"),Changed);
    Result.Add(TEXT("MaxRaiseCm"),FMath::RoundToInt(MaxRaise));Result.Add(TEXT("MaxLowerCm"),FMath::RoundToInt(MaxLower));
#endif
    return Result;
}

TMap<FString,FString> URVWorldContentLibrary::AuditRegionTerrain(UObject* Context)
{
    TMap<FString,FString> Result;
#if WITH_EDITOR
    UWorld* World=Context?Context->GetWorld():nullptr;
    if(!World || World->IsGameWorld() || !World->GetPackage()->GetName().EndsWith(TEXT("/WNY_PrototypeRegion")))return Result;
    ALandscape* Terrain=nullptr;for(TActorIterator<ALandscape> It(World);It;++It)Terrain=*It;
    if(!Terrain || !Terrain->GetLandscapeInfo())return Result;
    FLandscapeEditDataInterface Edit(Terrain->GetLandscapeInfo());
    const FVector2D Samples[]={{-62600,-5400},{-60000,-7000},{-62500,-6500},{-60000,-11000},{-60000,0}};
    for(const auto& P:Samples)
    {
        const FVector Local=Terrain->GetActorTransform().InverseTransformPosition(FVector(P.X,P.Y,0));
        const int32 X=FMath::RoundToInt(Local.X),Y=FMath::RoundToInt(Local.Y);
        uint16 Height=0;Edit.GetHeightDataFast(X,Y,X,Y,&Height,1);
        FString Value=FString::Printf(TEXT("Vertex=(%d,%d);Raw=%u;TextureZ=%.3f"),X,Y,Height,(int32(Height)-32768)*100./128.);
        for(TActorIterator<ALandscapeProxy> It(World);It;++It)
            if(const auto Cached=It->GetHeightAtLocation(FVector(P.X,P.Y,0));Cached.IsSet())Value+=FString::Printf(TEXT(";CollisionZ=%.3f;Proxy=%s"),Cached.GetValue(),*It->GetName());
        FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(RVRegionTerrainAudit),false);
        if(World->LineTraceSingleByChannel(Hit,FVector(P.X,P.Y,3000),FVector(P.X,P.Y,-4000),ECC_Visibility,Params))
            Value+=FString::Printf(TEXT(";RayZ=%.3f;Actor=%s"),Hit.ImpactPoint.Z,*GetNameSafe(Hit.GetActor()));
        Result.Add(FString::Printf(TEXT("%.0f,%.0f"),P.X,P.Y),Value);
    }
#endif
    return Result;
}

FString URVWorldContentLibrary::AuditRegionTerrainSamples(UObject* Context,const TArray<FVector2D>& Points)
{
#if WITH_EDITOR
    UWorld* World=Context?Context->GetWorld():nullptr;
    if(!World || World->IsGameWorld() || !World->GetPackage()->GetName().EndsWith(TEXT("/WNY_PrototypeRegion")))return FString();
    ALandscape* Terrain=nullptr;int32 Landscapes=0;for(TActorIterator<ALandscape> It(World);It;++It){Terrain=*It;++Landscapes;}
    ULandscapeInfo* Info=Terrain?Terrain->GetLandscapeInfo():nullptr;int32 MinX,MinY,MaxX,MaxY;
    if(!Info || !Info->GetLandscapeExtent(MinX,MinY,MaxX,MaxY) || MaxX-MinX>2048 || MaxY-MinY>2048)return FString();
    const int32 Width=MaxX-MinX+1,Height=MaxY-MinY+1;const FTransform Transform=Terrain->GetActorTransform();
    // Read-only copies: the final merged heightmap (invalid GUID) and every edit layer's own heightmap.
    struct FGrid{FGuid Guid;FString Name;TArray<uint16> Data;};TArray<FGrid> Grids;
    auto Read=[&](const FGuid& Guid,const FString& Name)
    {
        FGrid& Grid=Grids.AddDefaulted_GetRef();Grid.Guid=Guid;Grid.Name=Name;Grid.Data.SetNumZeroed(Width*Height);
        FLandscapeEditDataInterface Edit(Info);Edit.SetEditLayer(Guid);Edit.GetHeightDataFast(MinX,MinY,MaxX,MaxY,Grid.Data.GetData(),Width);
    };
    Read(FGuid(),TEXT("Final"));
    FString Layers;int32 LayerIndex=0;
    for(const ULandscapeEditLayerBase* Layer:Terrain->GetEditLayersConst())
    {
        if(!Layer){++LayerIndex;continue;}
        Read(Layer->GetGuid(),Layer->GetName().ToString());
        int32 ComponentsWithData=0;
        for(TActorIterator<ALandscapeProxy> It(World);It;++It)for(const auto& Component:It->LandscapeComponents)
            if(Component && Component->GetLayerData(Layer->GetGuid()))++ComponentsWithData;
        Layers+=FString::Printf(TEXT("%s{\"Index\":%d,\"Name\":\"%s\",\"Guid\":\"%s\",\"Class\":\"%s\",\"Visible\":%s,\"Locked\":%s,\"HeightAlpha\":%.3f,\"ComponentsWithData\":%d}"),
            Layers.IsEmpty()?TEXT(""):TEXT(","),LayerIndex++,*Layer->GetName().ToString(),*Layer->GetGuid().ToString(),*GetNameSafe(Layer->GetClass()),
            Layer->IsVisible()?TEXT("true"):TEXT("false"),Layer->IsLocked()?TEXT("true"):TEXT("false"),Layer->GetAlphaForTargetType(ELandscapeToolTargetType::Heightmap),ComponentsWithData);
    }
    int32 Components=0,SplineControlPoints=0;TArray<const AActor*> Proxies;
    for(TActorIterator<ALandscapeProxy> It(World);It;++It)
    {
        Proxies.Add(*It);Components+=It->LandscapeComponents.Num();
        if(const auto* Splines=It->GetSplinesComponent())SplineControlPoints+=Splines->GetControlPoints().Num();
    }
    FString Json=FString::Printf(TEXT("{\"Landscapes\":%d,\"Proxies\":%d,\"Components\":%d,\"Extent\":[%d,%d,%d,%d],\"EditingLayer\":\"%s\",\"LandscapeSplineControlPoints\":%d,\"Tags\":\"%s\",\"EditLayers\":[%s],\"Samples\":["),
        Landscapes,Proxies.Num(),Components,MinX,MinY,MaxX,MaxY,*Terrain->GetEditingLayer().ToString(),SplineControlPoints,
        *FString::JoinBy(Terrain->Tags,TEXT("|"),[](const FName& Tag){return Tag.ToString();}),*Layers);
    FCollisionQueryParams Any(SCENE_QUERY_STAT(RVRegionTerrainSamples),false),NonLandscape=Any;NonLandscape.AddIgnoredActors(Proxies);
    for(int32 Index=0;Index<Points.Num();++Index)
    {
        const FVector2D P=Points[Index];const FVector Local=Transform.InverseTransformPosition(FVector(P.X,P.Y,0));
        const int32 X0=FMath::FloorToInt(Local.X),Y0=FMath::FloorToInt(Local.Y);const double FX=Local.X-X0,FY=Local.Y-Y0;
        FString Sample=FString::Printf(TEXT("%s{\"X\":%.1f,\"Y\":%.1f"),Index?TEXT(","):TEXT(""),P.X,P.Y);
        if(X0>=MinX && Y0>=MinY && X0<MaxX && Y0<MaxY)for(const FGrid& Grid:Grids)
        {
            auto At=[&](int32 X,int32 Y){return LandscapeDataAccess::GetLocalHeight(Grid.Data[(Y-MinY)*Width+X-MinX]);};
            // Triangulated like Chaos heightfield collision, so texture and collision samples are directly comparable.
            const double LocalZ=FX<FY?At(X0,Y0)*(1-FY)+At(X0+1,Y0+1)*FX+At(X0,Y0+1)*(FY-FX):At(X0,Y0)*(1-FX)+At(X0+1,Y0)*(FX-FY)+At(X0+1,Y0+1)*FY;
            Sample+=FString::Printf(TEXT(",\"%sZ\":%.3f"),*Grid.Name,Transform.TransformPosition(FVector(Local.X,Local.Y,LocalZ)).Z);
        }
        for(const AActor* Proxy:Proxies)
            if(const auto Z=CastChecked<ALandscapeProxy>(Proxy)->GetHeightAtLocation(FVector(P.X,P.Y,0));Z.IsSet()){Sample+=FString::Printf(TEXT(",\"CollisionZ\":%.3f"),Z.GetValue());break;}
        FHitResult Hit;
        if(World->LineTraceSingleByChannel(Hit,FVector(P.X,P.Y,6000),FVector(P.X,P.Y,-6000),ECC_Visibility,Any))
            Sample+=FString::Printf(TEXT(",\"FirstHitZ\":%.3f,\"FirstHitActor\":\"%s\""),Hit.ImpactPoint.Z,*GetNameSafe(Hit.GetActor()));
        if(World->LineTraceSingleByChannel(Hit,FVector(P.X,P.Y,6000),FVector(P.X,P.Y,-6000),ECC_Visibility,NonLandscape))
            Sample+=FString::Printf(TEXT(",\"MeshZ\":%.3f,\"MeshActor\":\"%s\",\"MeshClass\":\"%s\""),Hit.ImpactPoint.Z,*GetNameSafe(Hit.GetActor()),*GetNameSafe(Hit.GetActor()?Hit.GetActor()->GetClass():nullptr));
        Json+=Sample+TEXT("}");
    }
    return Json+TEXT("]}");
#else
    return FString();
#endif
}
