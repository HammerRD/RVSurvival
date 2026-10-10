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
#include "LandscapeEdit.h"
#include "LandscapeComponent.h"
#include "LandscapeEditLayer.h"
#include "LandscapeDataAccess.h"
#include "LandscapeSplinesComponent.h"
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
    ALandscape* Landscape=nullptr;
    for(TActorIterator<ALandscape> It(World);It;++It){if(Landscape)return Result;Landscape=*It;}
    const FName Marker=bExtendGarage?TEXT("WNYGarageApproachV2"):TEXT("WNYGradedSitesV1");
    if(!Landscape || Landscape->ActorHasTag(Marker))return Result;
    if(bExtendGarage && !Landscape->ActorHasTag(TEXT("WNYGradedSitesV1")))return Result;
    auto* Info=Landscape->GetLandscapeInfo();int32 MinX,MinY,MaxX,MaxY;
    if(!Info || !Info->GetLandscapeExtent(MinX,MinY,MaxX,MaxY) || MaxX-MinX>2048 || MaxY-MinY>2048)return Result;
    const auto OriginalHeight=[](double X,double Y)
    {return (1800*FMath::Sin(X/65000)*FMath::Cos(Y/72000)+650*FMath::Sin(Y/25000))*FMath::Clamp((FMath::Abs(Y)-3000)/12000,0.,1.);};
    struct FSite{FVector2D Center,Half;double Height;};
    TArray<FSite> Sites={{{-130000,4900},{2500,2900},0},{{-60000,-5500},{3000,4100},0},
        {{0,46000},{2800,3500},OriginalHeight(0,45000)},{{75000,46000},{2800,3500},OriginalHeight(75000,45000)},
        {{140000,5000},{2500,3900},0}};
    if(bExtendGarage)Sites={{{-60000,-7000},{4000,6600},0}};
    const double Falloff=bExtendGarage?9000.:1400.;
    for(TActorIterator<ALandscapeProxy> It(World);It;++It)
    {It->Modify();for(const auto& Component:It->LandscapeComponents)if(Component)Component->Modify();}
    const int32 Width=MaxX-MinX+1;TArray<uint16> Heights;Heights.SetNumUninitialized(Width*(MaxY-MinY+1));
    FLandscapeEditDataInterface Edit(Info);Edit.GetHeightDataFast(MinX,MinY,MaxX,MaxY,Heights.GetData(),Width);
    for(const uint16 Height:Heights)if(Height<28000 || Height>38000)return Result; // Refuse unloaded/missing terrain samples.
    int32 Changed=0;
    for(int32 Y=MinY;Y<=MaxY;++Y)for(int32 X=MinX;X<=MaxX;++X)
    {
        const FVector P=Landscape->GetActorTransform().TransformPosition(FVector(X,Y,0));
        const int32 Index=(Y-MinY)*Width+X-MinX;double Height=(int32(Heights[Index])-32768)*100./128.;
        for(const auto& Site:Sites)
        {
            const double Outside=FMath::Max(FMath::Abs(P.X-Site.Center.X)-Site.Half.X,FMath::Abs(P.Y-Site.Center.Y)-Site.Half.Y);
            const double Alpha=FMath::SmoothStep(0.,1.,FMath::Clamp(1.-FMath::Max(0.,Outside)/Falloff,0.,1.));
            Height=FMath::Lerp(Height,Site.Height,Alpha);
        }
        const uint16 Value=uint16(FMath::Clamp(FMath::RoundToInt(32768.+Height*128./100.),0,65535));
        if(Value!=Heights[Index]){Heights[Index]=Value;++Changed;}
    }
    // Native edit updates height textures, normals, bounds and walkable collision.
    Edit.SetHeightData(MinX,MinY,MaxX,MaxY,Heights.GetData(),Width,true);Edit.Flush();
    Landscape->Tags.Add(Marker);Landscape->MarkPackageDirty();
    for(TActorIterator<ALandscapeProxy> It(World);It;++It)It->MarkPackageDirty();
    Result.Add(TEXT("ChangedVertices"),Changed);Result.Add(TEXT("GradedSites"),Sites.Num());
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
            const double LocalZ=FMath::Lerp(FMath::Lerp(At(X0,Y0),At(X0+1,Y0),FX),FMath::Lerp(At(X0,Y0+1),At(X0+1,Y0+1),FX),FY);
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
