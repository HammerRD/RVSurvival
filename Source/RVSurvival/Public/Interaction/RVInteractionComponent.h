#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RVInteractionComponent.generated.h"
/** Local camera focus for presentation; server retraces and validates every action.
 * Clients never nominate a target or send an outcome. Only the owning pawn can RPC. */
UCLASS(ClassGroup=(RV), meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVInteractionComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVInteractionComponent();
    void BeginInteraction();
    void EndInteraction();
    bool HasActiveInteraction() const { return ActiveTarget.IsValid(); }
    UFUNCTION(BlueprintPure, Category="RV|Interaction") FText GetPrompt() const;
    UFUNCTION(BlueprintPure, Category="RV|Interaction", meta=(DevelopmentOnly)) FString DebugTraceDescription() const;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
protected:
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    UPROPERTY(EditDefaultsOnly, Category="RV|Interaction", meta=(ClampMin="1")) float Range = 300.f;
    UPROPERTY(EditDefaultsOnly, Category="RV|Interaction", meta=(ClampMin="0.05")) float RequestInterval = 0.15f;
private:
    AActor* TraceTarget() const;
    bool IsAllowed(AActor* Target) const;
    void FinishInteraction();
    void CancelActive();
    UFUNCTION(Server, Reliable) void ServerBeginInteraction();
    UFUNCTION(Server, Reliable) void ServerEndInteraction();
    TWeakObjectPtr<AActor> FocusedTarget;
    TWeakObjectPtr<AActor> ActiveTarget;
    FTimerHandle CompletionTimer;
    double LastRequestTime = -1.e9;
};
