#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RVPassengerReferenceFrameComponent.generated.h"
/** Observes native CharacterMovement bases; does not attach or teleport a walking pawn. */
UCLASS(ClassGroup=(RV), meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVPassengerReferenceFrameComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVPassengerReferenceFrameComponent();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* TickFunction) override;
    UPROPERTY(BlueprintReadOnly, Category="RV|Passenger") TObjectPtr<AActor> ReferenceFrame;
    UPROPERTY(BlueprintReadOnly, Category="RV|Passenger") FVector LocalPosition = FVector::ZeroVector;
    UPROPERTY(BlueprintReadOnly, Category="RV|Passenger") int32 FrameChanges = 0;
    UPROPERTY(BlueprintReadOnly, Category="RV|Debug") TObjectPtr<class UPrimitiveComponent> CurrentBase;
    UPROPERTY(BlueprintReadOnly, Category="RV|Debug") int32 BaseChanges = 0;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="RV|Passenger", meta=(ClampMin="1")) float InteriorCapsuleRadius = 30.f;
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="RV|Passenger", meta=(ClampMin="1")) float InteriorWalkSpeed = 200.f;
    UPROPERTY(BlueprintReadOnly, Category="RV|Debug") int32 CorrectionCount = 0;
    UPROPERTY(BlueprintReadOnly, Category="RV|Debug") float MaxCorrectionCm = 0;
    UPROPERTY(BlueprintReadOnly, Category="RV|Debug") float MaxLocalStepCm = 0;
    void RecordCorrection(float Distance);
    float GetOutsideCapsuleRadius() const { return ReferenceFrame ? PreviousCapsuleRadius : 0.f; }
    UFUNCTION(BlueprintCallable, Category="RV|Debug") void ResetDiagnostics();
private:
    void RestoreWorldMovement();
    float PreviousCapsuleRadius = 0;
    float PreviousWalkSpeed = 0;
    bool bPreviousPhysicsInteraction = true;
    bool bPreviousIgnorePhysicsBase = false;
};
