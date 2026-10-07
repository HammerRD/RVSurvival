#pragma once
#include "CoreMinimal.h"
#include "Vehicles/RVVehicleBase.h"
#include "RVMotorhome.generated.h"
/** First concrete RV. Rig/physics/animation are replaceable Blueprint configuration. */
UCLASS(Blueprintable)
class RVSURVIVAL_API ARVMotorhome : public ARVVehicleBase
{
    GENERATED_BODY()
public:
    ARVMotorhome(const FObjectInitializer& Initializer);
    void OrbitCamera(float Yaw,float Pitch);
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="RV|Seats") TObjectPtr<class URVVehicleSeatComponent> DriverSeat;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="RV|Seats") TObjectPtr<class URVVehicleSeatComponent> PassengerSeat;
protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="RV|Prototype") TObjectPtr<class UStaticMeshComponent> PrototypeBody;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="RV|Prototype") TObjectPtr<class UStaticMeshComponent> PrototypeCab;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="RV|Camera") TObjectPtr<class USpringArmComponent> CameraArm;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="RV|Camera") TObjectPtr<class UCameraComponent> DrivingCamera;
};
