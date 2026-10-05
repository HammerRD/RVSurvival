#include "Vehicles/RVVehicleWheel.h"
URVVehicleWheelFront::URVVehicleWheelFront()
{
    AxleType = EAxleType::Front; WheelRadius = 50; WheelWidth = 30;
    bAffectedBySteering = true; MaxSteerAngle = 32; bAffectedByEngine = false;
    SuspensionMaxRaise = 10; SuspensionMaxDrop = 20; SpringRate = 1000; SuspensionDampingRatio = 0.7f;
}
URVVehicleWheelRear::URVVehicleWheelRear()
{
    AxleType = EAxleType::Rear; WheelRadius = 50; WheelWidth = 30;
    bAffectedBySteering = false; bAffectedByEngine = true; bAffectedByHandbrake = true;
    SuspensionMaxRaise = 10; SuspensionMaxDrop = 20; SpringRate = 1000; SuspensionDampingRatio = 0.7f;
}
