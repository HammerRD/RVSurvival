#pragma once
#include "CoreMinimal.h"
#include "ChaosVehicleWheel.h"
#include "RVVehicleWheel.generated.h"
UCLASS()
class RVSURVIVAL_API URVVehicleWheelFront : public UChaosVehicleWheel
{ GENERATED_BODY() public: URVVehicleWheelFront(); };
UCLASS()
class RVSURVIVAL_API URVVehicleWheelRear : public UChaosVehicleWheel
{ GENERATED_BODY() public: URVVehicleWheelRear(); };
