#pragma once
#include "CoreMinimal.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "RVVehicleMovementComponent.generated.h"
/** Server-only Chaos force simulation. Inputs arrive through the owning controller. */
UCLASS()
class RVSURVIVAL_API URVVehicleMovementComponent : public UChaosWheeledVehicleMovementComponent
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void PreTickGT(float DeltaTime) override;
    virtual void Update(float DeltaTime) override;
protected:
    virtual bool ShouldCreatePhysicsState() const override;
    virtual void FixupSkeletalMesh() override;
    virtual void ServerUpdateState_Implementation(float Steering, float Throttle, float Brake, float Handbrake,
        int32 Gear, float Roll, float Pitch, float Yaw) override;
};
