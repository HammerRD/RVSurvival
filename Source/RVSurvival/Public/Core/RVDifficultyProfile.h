#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "RVDifficultyProfile.generated.h"

/** Serializable world rules. Personal input/display settings never enter this snapshot. */
USTRUCT(BlueprintType)
struct FRVDifficultyRule
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName Id;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FText Label;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FText Description;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName Group;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float Minimum=.25f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float Maximum=3.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float Multiplier=1.f;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) bool bPreparationOnly=false;
};

UCLASS(BlueprintType)
class RVSURVIVAL_API URVDifficultyProfile : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    URVDifficultyProfile();
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) FName Preset=TEXT("Standard");
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TArray<FRVDifficultyRule> Rules;
};

/** Engine config-backed client preferences, independent of authoritative world rules. */
UCLASS(Config=GameUserSettings)
class RVSURVIVAL_API URVPersonalSettings : public UObject
{
    GENERATED_BODY()
public:
    UPROPERTY(Config) float LookSensitivity=1.f;
    UPROPERTY(Config) bool bInvertLook=false;
    void ApplyAndSave() { LookSensitivity=FMath::Clamp(LookSensitivity,.1f,3.f); SaveConfig(); }
};
