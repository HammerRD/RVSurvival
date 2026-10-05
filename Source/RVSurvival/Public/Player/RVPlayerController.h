#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "RVPlayerController.generated.h"
class ARVVehicleBase;
/** Gate 1 framework boundary; later gates add only the state owned by this role. */
UCLASS()
class RVSURVIVAL_API ARVPlayerController : public APlayerController
{
    GENERATED_BODY()
public:
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual void PawnLeavingGame() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    UFUNCTION(Server, Unreliable) void ServerDrive(float Throttle, float Steering, bool Handbrake);
    UFUNCTION(Server, Reliable) void ServerExitVehicle();
    UPROPERTY(Replicated, BlueprintReadOnly, Category="RV|Seats") TObjectPtr<ARVVehicleBase> SeatedVehicle;
    double SeatEntryTime = 0;
};
