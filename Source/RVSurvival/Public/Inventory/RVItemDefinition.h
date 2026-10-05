#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameplayTagContainer.h"
#include "RVItemDefinition.generated.h"

/** Immutable catalog data. Stored instances reference definitions rather than world actors. */
UCLASS(BlueprintType)
class RVSURVIVAL_API URVItemDefinition : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintPure, Category="RV|Items") static FGameplayTag FindRegisteredTag(FName Name);
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FName CatalogId;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FText DisplayName;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(MultiLine=true)) FText Description;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FGameplayTag Category;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FGameplayTagContainer Tags;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FGameplayTagContainer CraftingTags;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TSoftObjectPtr<UStaticMesh> WorldMesh;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TSoftObjectPtr<UTexture2D> Icon;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0")) float WeightKg = 1;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0")) float VolumeLitres = 1;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bStackable = false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="1")) int32 MaxStackSize = 1;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bSupportsCondition = false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bEquippable = false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bRequiresPhysicalCarry = false;
};
