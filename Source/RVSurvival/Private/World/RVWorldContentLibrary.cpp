#include "World/RVWorldContentLibrary.h"
#include "World/RVScavengeContainer.h"
#include "World/RVRegionStateSubsystem.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#if WITH_EDITOR
#include "Landscape.h"
#include "LandscapeInfo.h"
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
