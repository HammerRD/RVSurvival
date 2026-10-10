#include "World/RVWorldContentLibrary.h"
#include "World/RVScavengeContainer.h"
#include "World/RVRegionStateSubsystem.h"
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
    TMap<FString,int32> Result;Result.Add(TEXT("Pending"),0);Result.Add(TEXT("Instances"),0);Result.Add(TEXT("Components"),0);
    if(auto* World=Context?Context->GetWorld():nullptr)
        for(TActorIterator<AActor> It(World);It;++It)
        {
            TArray<UPCGComponent*> PCG;It->GetComponents(PCG);
            for(auto* C:PCG){++Result[TEXT("Components")];if(C->IsGenerating())++Result[TEXT("Pending")];}
            TArray<UInstancedStaticMeshComponent*> Instances;It->GetComponents(Instances);
            for(auto* C:Instances)Result[TEXT("Instances")]+=C->GetInstanceCount();
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
