#include "World/RVScavengeContainer.h"
#include "World/RVRegionStateSubsystem.h"
#include "Core/RVGameState.h"
#include "Engine/World.h"
#include "Net/UnrealNetwork.h"

ARVScavengeContainer::ARVScavengeContainer()
{
    bAlwaysRelevant=false;
    SetNetCullDistanceSquared(FMath::Square(20000.f));
}
void ARVScavengeContainer::BeginPlay()
{
    Super::BeginPlay();
    if(!HasAuthority()) return;
    auto* Ledger=GetWorld()->GetSubsystem<URVRegionStateSubsystem>();
    bOwnsIdentity=Ledger && Ledger->Claim(ContainerId,this);
    if(!bOwnsIdentity)
    {
        UE_LOG(LogTemp,Error,TEXT("Scavenge container %s needs a unique authored GUID; refusing loot"),*GetName());
        return;
    }
    auto& Record=Ledger->Containers.FindOrAdd(ContainerId);
    bSearched=Record.bSearched;
    FString Error;
    if(Record.bGenerated)
    {
        const auto Retained=Container->GetItems();
        for(const auto& Item:Record.Items)
            if(!Retained.ContainsByPredicate([&Item](const auto& Existing){return Existing.Id==Item.Id;})
                && !Container->AddAuthority(Item,Error))
            {
                bRestoreIncomplete=true;
                UE_LOG(LogTemp,Error,TEXT("Unable to restore %s; preserving ledger snapshot: %s"),*GetName(),*Error);
            }
        return;
    }
    // Mark even an empty result as generated; revisiting never rerolls depleted supplies.
    Record.bGenerated=true;
    if(!LootProfile) return;
    FRandomStream Random(GetTypeHash(ContainerId));
    const float Abundance=FMath::Clamp(ARVGameState::Multiplier(this,TEXT("Loot"))*LootProfile->RegionalAbundance,0.f,9.f);
    for(const auto& Entry:LootProfile->Entries)
    {
        if(!Entry.Definition || !FMath::IsFinite(Entry.Chance) || !FMath::IsFinite(Entry.MinimumCondition)
            || !FMath::IsFinite(Entry.MaximumCondition) || Entry.MinimumQuantity<1 || Entry.MinimumQuantity>100 || Entry.MaximumQuantity<Entry.MinimumQuantity)
            continue;
        if(Random.FRand()>=FMath::Clamp(Entry.Chance*Abundance,0.f,1.f)) continue;
        int32 Remaining=Random.RandRange(Entry.MinimumQuantity,FMath::Min(Entry.MaximumQuantity,100));
        while(Remaining>0)
        {
            FRVItemInstance Item;Item.Id=FGuid::NewGuid();Item.Definition=Entry.Definition;
            Item.Quantity=FMath::Min(Remaining,Entry.Definition->bStackable?FMath::Max(1,Entry.Definition->MaxStackSize):1);
            Item.Condition=Random.FRandRange(FMath::Clamp(Entry.MinimumCondition,0.f,1.f),
                FMath::Clamp(FMath::Max(Entry.MinimumCondition,Entry.MaximumCondition),0.f,1.f));
            if(!Container->AddAuthority(Item,Error)) break;
            Remaining-=Item.Quantity;
        }
    }
    Record.Items=Container->GetItems();
}
void ARVScavengeContainer::EndPlay(const EEndPlayReason::Type Reason)
{
    if(HasAuthority() && bOwnsIdentity)
        if(auto* Ledger=GetWorld()->GetSubsystem<URVRegionStateSubsystem>())
        {
            auto& Record=Ledger->Containers.FindOrAdd(ContainerId);
            if(!bRestoreIncomplete) Record.Items=Container->GetItems();
            Record.bSearched=bSearched;
            Ledger->Release(ContainerId,this);
        }
    Super::EndPlay(Reason);
}
bool ARVScavengeContainer::CanInteract_Implementation(APawn* Pawn) const
{return Super::CanInteract_Implementation(Pawn) && (!HasAuthority() || (bOwnsIdentity && !bRestoreIncomplete));}
void ARVScavengeContainer::CompleteInteraction_Implementation(APawn* Pawn)
{
    if(!HasAuthority() || !CanInteract_Implementation(Pawn)) return;
    bSearched=true;
    if(auto* Ledger=GetWorld()->GetSubsystem<URVRegionStateSubsystem>())
        Ledger->Containers.FindOrAdd(ContainerId).bSearched=true;
    Super::CompleteInteraction_Implementation(Pawn);ForceNetUpdate();
}
void ARVScavengeContainer::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(ARVScavengeContainer,bSearched);}
