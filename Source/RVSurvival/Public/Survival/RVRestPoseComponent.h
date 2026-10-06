#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RVRestPoseComponent.generated.h"
class ARVRestPoint;
/** Reserved rest anchor and replaceable prototype lying presentation; never drives walking transforms. */
UCLASS(ClassGroup=(RV),meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVRestPoseComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVRestPoseComponent();
    virtual void BeginPlay() override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    bool BeginPoseAuthority(ARVRestPoint* Point);
    bool EndPoseAuthority(bool bForceCleanup=false);
    UPROPERTY(ReplicatedUsing=OnRep_RestPoint,BlueprintReadOnly) TObjectPtr<ARVRestPoint> RestPoint;
private:
    UFUNCTION() void OnRep_RestPoint();
    UPROPERTY(Transient) TObjectPtr<class UStaticMeshComponent> PrototypeBody;
    UPROPERTY(Transient) TObjectPtr<class UStaticMeshComponent> PrototypeHead;
    FTransform PreviousMeshTransform;
    FVector PreviousCameraLocation;
    float PreviousEyeHeight=64;
    bool bPresentationActive=false;
};
