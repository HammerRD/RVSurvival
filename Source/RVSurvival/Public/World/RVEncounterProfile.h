#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "GameplayTagContainer.h"
#include "RVEncounterProfile.generated.h"
UENUM(BlueprintType)
enum class ERVEncounterOutcome : uint8 { Quiet, InfectedCluster, SupplyCache };
USTRUCT(BlueprintType)
struct FRVEncounterChoice
{
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadOnly) ERVEncounterOutcome Outcome=ERVEncounterOutcome::Quiet;
 UPROPERTY(EditAnywhere,BlueprintReadOnly,meta=(ClampMin="0")) float Weight=1;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) int32 InfectedCount=2;
};
/** Contextual pacing data, not a replacement for native AI/perception/navigation. */
UCLASS(BlueprintType)
class RVSURVIVAL_API URVEncounterProfile : public UPrimaryDataAsset
{
 GENERATED_BODY()
public:
 UPROPERTY(EditAnywhere,BlueprintReadOnly) FGameplayTag Context;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) TArray<FRVEncounterChoice> Choices;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) TObjectPtr<class URVInfectedProfile> InfectedProfile;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) TObjectPtr<class URVLootProfile> SupplyProfile;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) float ActiveRadius=15000;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) float ReleaseRadius=22000;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) float MinimumSpawnDistance=2500;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) float EventCooldown=150;
};
