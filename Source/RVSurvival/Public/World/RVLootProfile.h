#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameplayTagContainer.h"
#include "Inventory/RVInventoryComponent.h"
#include "RVLootProfile.generated.h"

USTRUCT(BlueprintType)
struct FRVLootEntry
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<URVItemDefinition> Definition;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="0",ClampMax="1")) float Chance=.5f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="1",ClampMax="100")) int32 MinimumQuantity=1;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="1",ClampMax="100")) int32 MaximumQuantity=1;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="0",ClampMax="1")) float MinimumCondition=.6f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="0",ClampMax="1")) float MaximumCondition=1.f;
};

/** Location-specific supply probabilities; uses accepted item definitions and capacities. */
UCLASS(BlueprintType)
class RVSURVIVAL_API URVLootProfile : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FGameplayTag Context;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="0",ClampMax="3")) float RegionalAbundance=1;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TArray<FRVLootEntry> Entries;
};
