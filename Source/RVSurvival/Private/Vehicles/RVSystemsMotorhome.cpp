#include "Vehicles/RVSystemsMotorhome.h"
#include "Resources/RVElectricalComponent.h"
#include "Vehicles/RVResourcePoint.h"
#include "Player/RVPlayerController.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/SkeletalMeshComponent.h"
ARVSystemsMotorhome::ARVSystemsMotorhome(const FObjectInitializer& Init):Super(Init)
{
    PropulsionFuel=CreateDefaultSubobject<URVFuelComponent>(TEXT("PropulsionFuel"));
    GeneratorFuel=CreateDefaultSubobject<URVFuelComponent>(TEXT("GeneratorFuel")); GeneratorFuel->CapacityLitres=30; GeneratorFuel->InitialLitres=20;
    HouseBattery=CreateDefaultSubobject<URVBatteryComponent>(TEXT("HouseBattery"));
    ChassisBattery=CreateDefaultSubobject<URVBatteryComponent>(TEXT("ChassisBattery"));
    ChassisBattery->Domain=ERVPowerDomain::Chassis; ChassisBattery->CapacityWh=800; ChassisBattery->InitialWh=600;
    ChassisBattery->MaxChargeWatts=250;
    Electrical=CreateDefaultSubobject<URVElectricalComponent>(TEXT("Electrical"));
    FrontLight=CreateDefaultSubobject<UPointLightComponent>(TEXT("InteriorFrontLight")); FrontLight->SetupAttachment(GetMesh());
    RearLight=CreateDefaultSubobject<UPointLightComponent>(TEXT("InteriorRearLight")); RearLight->SetupAttachment(GetMesh());
    FrontLight->SetRelativeLocation(FVector(110,0,250)); RearLight->SetRelativeLocation(FVector(-180,0,270));
    for(auto* Light:{FrontLight.Get(),RearLight.Get()})
    { Light->SetIntensity(1000); Light->SetAttenuationRadius(350); Light->SetLightColor(FLinearColor(1,.85,.65)); Light->SetCastShadows(false); Light->SetVisibility(false); }
}
void ARVSystemsMotorhome::BeginPlay()
{
    Super::BeginPlay();
    ConfiguredEngineTorque=CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement())->EngineSetup.MaxTorque;
    if(HasAuthority())
    {
        for(bool Fill:{true,false})
        {
            auto* Point=GetWorld()->SpawnActorDeferred<ARVResourcePoint>(ARVResourcePoint::StaticClass(),GetActorTransform(),this);
            Point->Vehicle=this; Point->bFuelFill=Fill; Point->FinishSpawning(GetActorTransform());
            Point->AttachToComponent(GetMesh(),FAttachmentTransformRules::SnapToTargetNotIncludingScale);
            Point->SetActorRelativeLocation(Fill?FuelFillLocation:PowerPanelLocation);
        }
    }
}
void ARVSystemsMotorhome::Tick(float DT)
{
    Super::Tick(DT);
    if(HasAuthority())
    {
        const bool Driver=IsDriver(Cast<ARVPlayerController>(GetController()));
        auto* Move=CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement());
        SimulationAccumulator+=DT;
        if(SimulationAccumulator>=.25)
        {
            const double Elapsed=SimulationAccumulator; SimulationAccumulator=0;
            Electrical->AdvanceAuthority(Elapsed*Electrical->TimeScale,Driver || Electrical->bEngineIdleRequested,Move->GetThrottleInput(),GetVelocity().Size());
        }
        // Gate both directions at the supported engine torque boundary. Braking/steering/physics persist.
        const bool CanPropel=PropulsionFuel->Litres>0;
        if(CanPropel!=bTorqueEnabled)
        { CastChecked<UChaosWheeledVehicleMovementComponent>(GetVehicleMovement())->SetMaxEngineTorque(CanPropel?ConfiguredEngineTorque:0); bTorqueEnabled=CanPropel; }
    }
    const bool LightOn=Electrical->IsLoadPowered(TEXT("InteriorLights"));
    FrontLight->SetVisibility(LightOn); RearLight->SetVisibility(LightOn);
}
