#include "Vehicles/RVMotorhome.h"
#include "Vehicles/RVVehicleSeatComponent.h"
#include "Vehicles/RVVehicleMovementComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Camera/CameraComponent.h"
#include "UObject/ConstructorHelpers.h"
ARVMotorhome::ARVMotorhome(const FObjectInitializer& Init) : Super(Init)
{
    DriverSeat = CreateDefaultSubobject<URVVehicleSeatComponent>(TEXT("DriverSeat")); DriverSeat->SetupAttachment(GetMesh());
    DriverSeat->bDriverSeat = true; DriverSeat->SeatLabel = NSLOCTEXT("RV", "Driver", "Driver");
    DriverSeat->SetRelativeLocation(FVector(90,-55,110)); DriverSeat->EntryOffset = FVector(90,-170,90); DriverSeat->ExitOffset = FVector(90,-300,0);
    PassengerSeat = CreateDefaultSubobject<URVVehicleSeatComponent>(TEXT("PassengerSeat")); PassengerSeat->SetupAttachment(GetMesh());
    PassengerSeat->SeatLabel = NSLOCTEXT("RV", "Passenger", "Passenger"); PassengerSeat->SetRelativeLocation(FVector(90,55,110));
    PassengerSeat->EntryOffset = FVector(90,170,90); PassengerSeat->ExitOffset = FVector(90,300,0);
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    PrototypeBody = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeRVBody")); PrototypeBody->SetupAttachment(GetMesh());
    PrototypeBody->SetStaticMesh(Cube.Object); PrototypeBody->SetRelativeLocation(FVector(-85,0,140)); PrototypeBody->SetRelativeScale3D(FVector(3.2,2.4,2.1));
    PrototypeBody->SetCollisionProfileName(TEXT("BlockAll")); PrototypeBody->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    PrototypeCab = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PrototypeRVCab")); PrototypeCab->SetupAttachment(GetMesh());
    PrototypeCab->SetStaticMesh(Cube.Object); PrototypeCab->SetRelativeLocation(FVector(130,0,90)); PrototypeCab->SetRelativeScale3D(FVector(1.1,2.4,1.1));
    PrototypeCab->SetCollisionProfileName(TEXT("BlockAll")); PrototypeCab->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    auto* Label = CreateDefaultSubobject<UTextRenderComponent>(TEXT("PrototypeLabel")); Label->SetupAttachment(GetMesh());
    Label->SetText(NSLOCTEXT("RV", "Prototype", "PROTOTYPE RV - GATE 2")); Label->SetWorldSize(20);
    Label->SetRelativeLocation(FVector(-220,-122,195)); Label->SetRelativeRotation(FRotator(0,-90,0));
    CameraArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("DrivingCameraArm")); CameraArm->SetupAttachment(GetMesh());
    CameraArm->TargetArmLength = 900; CameraArm->SocketOffset = FVector(0,0,280);
    CameraArm->bInheritRoll = false; CameraArm->bInheritPitch = false; CameraArm->bDoCollisionTest = true;
    DrivingCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("DrivingCamera")); DrivingCamera->SetupAttachment(CameraArm);
    auto* Movement = CastChecked<URVVehicleMovementComponent>(GetVehicleMovement());
    Movement->Mass = 3500; Movement->bEnableCenterOfMassOverride = true; Movement->CenterOfMassOverride = FVector(0,0,10);
    Movement->EngineSetup.MaxTorque = 850; Movement->EngineSetup.MaxRPM = 4500; Movement->EngineSetup.EngineIdleRPM = 800;
    auto* Curve = Movement->EngineSetup.TorqueCurve.GetRichCurve();
    Curve->AddKey(0, .4f); Curve->AddKey(1500, 1); Curve->AddKey(3000, .9f); Curve->AddKey(4500,.5f);
    Movement->DifferentialSetup.DifferentialType = EVehicleDifferential::RearWheelDrive;
    Movement->TransmissionSetup.bUseAutomaticGears = true; Movement->TransmissionSetup.bUseAutoReverse = true;
    Movement->bReverseAsBrake = true;
}
