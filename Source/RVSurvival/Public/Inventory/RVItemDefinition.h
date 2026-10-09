#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameplayTagContainer.h"
#include "Medical/RVMedicalProfile.h"
#include "RVItemDefinition.generated.h"

USTRUCT(BlueprintType)
struct FRVConsumableMetadata
{
    GENERATED_BODY()
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bConsumable = false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0")) float Nutrition = 0;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0")) float Hydration = 0;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0",ClampMax="1")) float MinimumCondition = 0;
    // Metadata only: no digestion, spoilage or cooking simulation in Gate 5.
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) float EnergyKcal = 0;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FGameplayTagContainer DietaryTags;
};

USTRUCT(BlueprintType)
struct FRVFuelContainerMetadata
{
    GENERATED_BODY()
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bFuelContainer = false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FGameplayTag FuelType;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0")) double CapacityLitres = 20;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0")) double InitialLitres = 20;
};

/** Immutable catalog data. Stored instances reference definitions rather than world actors. */
USTRUCT(BlueprintType)
struct FRVCombatItemMetadata
{
    GENERATED_BODY()
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bFirearm=false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bMelee=false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bMagazine=false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<class URVWeaponPresentationProfile> Presentation;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bQuickAccess=false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) int32 QuickAccessOrder=100;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FGameplayTag Caliber;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="1")) int32 MagazineCapacity=15;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0")) int32 InitialRounds=15;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0.1")) float ShotInterval=.25f;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0.1")) float ReloadSeconds=2;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="1")) float RangeCm=10000;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0")) float Damage=30;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly,meta=(ClampMin="0")) float HeadDamageMultiplier=2;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly,meta=(ClampMin="0")) float LimbDamageMultiplier=.75f;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly,meta=(ClampMin="1",ClampMax="3")) float WoundSeverity=2;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly,meta=(ClampMin="0")) float RecoilPitch=.7f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="0")) float RecoilYaw=.12f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="0.05")) float RecoilRecoverySeconds=.18f;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly,meta=(ClampMin="0")) float HearingRange=5000;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FName HandAnchor=TEXT("Tool");
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FTransform GripOffset;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FTransform FirstPersonOffset;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FTransform ThirdPersonOffset;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FTransform SupportHandTarget;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FTransform HolsterOffset;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FName MuzzleSocket;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FTransform MuzzleTransform=FTransform(FVector(12,0,0));
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FTransform EjectTransform;
    // Camera-relative weapon transform is solved from this actual sight reference.
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bSightADS=false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FTransform SightTransform;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly,meta=(ClampMin="1",ClampMax="80")) float SightEyeReliefCm=10;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly,meta=(ClampMin="1",ClampMax="30")) float AimBlendSpeed=12;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly,meta=(ClampMin=".4",ClampMax="1")) float SightFOVScale=.8f;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly,meta=(ClampMin="1",ClampMax="200")) float MeleeRangeCm=160;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly,meta=(ClampMin="0",ClampMax="20")) float MeleeSweepRadiusCm=10;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly,meta=(ClampMin=".3",ClampMax="5")) float MeleeCooldownSeconds=.9f;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly,meta=(ClampMin="0",ClampMax="10")) float MeleeFatigueCost=.3f;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<class UAnimMontage> MeleeMontage;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<class USoundBase> ShotSound;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) TObjectPtr<class UMaterialInterface> ShotEffectMaterial;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<class UAnimMontage> FireMontage;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TObjectPtr<class UAnimMontage> ReloadMontage;
};

UCLASS(BlueprintType)
class RVSURVIVAL_API URVItemDefinition : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FRVCombatItemMetadata Combat;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FRVMedicalSupplyMetadata Medical;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FRVConsumableMetadata Consumable;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FRVFuelContainerMetadata Fuel;
    UFUNCTION(BlueprintPure, Category="RV|Items") static FGameplayTag FindRegisteredTag(FName Name);
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FName CatalogId;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FText DisplayName;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(MultiLine=true)) FText Description;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FGameplayTag Category;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FGameplayTagContainer Tags;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FGameplayTagContainer CraftingTags;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TSoftObjectPtr<UStaticMesh> WorldMesh;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) FVector WorldVisualScale=FVector(.2f);
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TSoftObjectPtr<UTexture2D> Icon;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0")) float WeightKg = 1;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0")) float VolumeLitres = 1;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bStackable = false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="1")) int32 MaxStackSize = 1;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bSupportsCondition = false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bEquippable = false;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) bool bRequiresPhysicalCarry = false;
    // Zero means a tap. Bulky/committed pickups can explicitly retain a hold.
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, meta=(ClampMin="0",ClampMax="60")) float PickupSeconds = 0;
};

