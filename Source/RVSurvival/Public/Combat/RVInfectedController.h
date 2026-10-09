#pragma once
#include "CoreMinimal.h"
#include "AIController.h"
#include "Perception/AIPerceptionTypes.h"
#include "BehaviorTree/BTTaskNode.h"
#include "RVInfectedController.generated.h"
/** Native perception/path following. RV policy lives in one inspectable BT task. */
UCLASS()
class RVSURVIVAL_API ARVInfectedController : public AAIController
{
    GENERATED_BODY()
public:
    ARVInfectedController();
    virtual void OnPossess(APawn* Pawn) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    void UpdateBehavior();
    UFUNCTION() void PerceptionChanged(AActor* Actor,FAIStimulus Stimulus);
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<class UAIPerceptionComponent> Senses;
private:
    UPROPERTY() TObjectPtr<class UAISenseConfig_Sight> Sight;
    UPROPERTY() TObjectPtr<class UAISenseConfig_Hearing> Hearing;
    UPROPERTY() TObjectPtr<class UBehaviorTree> Behavior;
    TWeakObjectPtr<AActor> VisibleTarget;
    FVector LastKnown=FVector::ZeroVector;
    FVector Home=FVector::ZeroVector;
    double InvestigateUntil=0;
    double NextWander=0;
    float PerceptionMultiplier=1;
};
UCLASS()
class RVSURVIVAL_API URVBTTask_Infected : public UBTTaskNode
{
    GENERATED_BODY()
public:
    URVBTTask_Infected();
    virtual EBTNodeResult::Type ExecuteTask(UBehaviorTreeComponent& OwnerComp,uint8* NodeMemory) override;
    virtual void TickTask(UBehaviorTreeComponent& OwnerComp,uint8* NodeMemory,float DeltaSeconds) override;
};
