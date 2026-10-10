#pragma once
#include "CoreMinimal.h"
#include "Inventory/RVWorldItem.h"
#include "World/RVLootProfile.h"
#include "RVScavengeContainer.generated.h"

/** Opt-in regional storage. Never changes accepted RV cabinets or old test maps. */
UCLASS()
class RVSURVIVAL_API ARVScavengeContainer : public ARVStoragePoint
{
    GENERATED_BODY()
public:
    ARVScavengeContainer();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual bool CanInteract_Implementation(APawn* Pawn) const override;
    virtual void CompleteInteraction_Implementation(APawn* Pawn) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    UPROPERTY(EditAnywhere,BlueprintReadOnly,SaveGame) FGuid ContainerId;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) TObjectPtr<URVLootProfile> LootProfile;
    UPROPERTY(Replicated,BlueprintReadOnly) bool bSearched=false;
private:
    bool bOwnsIdentity=false;
};
