#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RVRecoveryComponent.generated.h"
class ARVPlayerController;
/** Prototype policy boundary; future equipment can replace permission/cost rules. */
UCLASS(ClassGroup=(RV),meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVRecoveryComponent : public UActorComponent
{
 GENERATED_BODY()
public:
 URVRecoveryComponent();
 virtual void TickComponent(float DT,ELevelTick Type,FActorComponentTickFunction* Function) override;
 virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out)const override;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) bool bPrototypeRecoveryEnabled=true;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) float MaximumUpDot=.35f;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) float MaximumSpeed=30;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) float MaximumAngularSpeedDegrees=5;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) float ConfirmationSeconds=3;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) float RequestRange=1000;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) float GroundClearance=45;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) FVector PlacementCenter=FVector(0,0,200);
 UPROPERTY(EditAnywhere,BlueprintReadOnly) FVector PlacementExtent=FVector(550,250,210);
 UPROPERTY(Replicated,BlueprintReadOnly) bool bConfirmedOverturned=false;
 UPROPERTY(Replicated,BlueprintReadOnly) int32 RecoveryRevision=0;
 UPROPERTY(Replicated,BlueprintReadOnly) double RecoveryGraceUntil=0;
 bool StopsPropulsion()const;
 bool RecoverAuthority(ARVPlayerController* Requester,FString& Feedback);
 UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly)) bool DebugOverturn(float Roll);
private:
 float StableTime=0;
};
