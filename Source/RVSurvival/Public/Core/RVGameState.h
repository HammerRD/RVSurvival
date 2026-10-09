#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameStateBase.h"
#include "Core/RVDifficultyProfile.h"
#include "RVGameState.generated.h"
/** Gate 1 framework boundary; later gates add only the state owned by this role. */
UCLASS()
class RVSURVIVAL_API ARVGameState : public AGameStateBase
{
    GENERATED_BODY()
public:
    ARVGameState();
    virtual void BeginPlay() override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly) TArray<TObjectPtr<URVDifficultyProfile>> DifficultyPresets;
    UPROPERTY(Replicated, BlueprintReadOnly) TArray<FRVDifficultyRule> DifficultyRules;
    UPROPERTY(Replicated, BlueprintReadOnly) FName DifficultyPreset=TEXT("Standard");
    UPROPERTY(Replicated, BlueprintReadOnly) int32 DifficultyRevision=0;
    static float Multiplier(const UObject* Context,FName Rule);
    bool SetDifficultyAuthority(FName Preset,FName Rule,float Value,int32 ExpectedRevision);
};
