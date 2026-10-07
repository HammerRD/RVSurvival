#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RVLadderClimbComponent.generated.h"
class ARVLadder;
/** Uses native CharacterMovement flying prediction; no custom physics or per-tick position forcing. */
UCLASS()
class RVSURVIVAL_API URVLadderClimbComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVLadderClimbComponent();
    virtual void TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Function) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    UPROPERTY(ReplicatedUsing=OnRep_Ladder,BlueprintReadOnly) TObjectPtr<ARVLadder> Ladder;
    UPROPERTY(Replicated,BlueprintReadOnly) TObjectPtr<ARVLadder> RoofLadder;
    bool BeginAuthority(ARVLadder* Target);
    bool EndAuthority();
    void ClimbInput(float Value);
    UFUNCTION(Server,Reliable) void ServerExit();
private:
    UFUNCTION() void OnRep_Ladder();
    float PreviousFlySpeed=600;
    bool bPreviousPlaneConstraint=false;
    bool bPreviousPhysicsInteraction=true;
    FVector PreviousPlaneNormal;
    FVector PreviousPlaneOrigin;
    bool bApplied=false;
};
