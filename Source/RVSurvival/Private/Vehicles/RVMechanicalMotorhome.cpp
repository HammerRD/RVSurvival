#include "Vehicles/RVMechanicalMotorhome.h"
#include "Mechanical/RVCoolingComponent.h"
#include "Mechanical/RVServicePoint.h"
#include "Net/UnrealNetwork.h"
#include "Components/SkeletalMeshComponent.h"
ARVMechanicalMotorhome::ARVMechanicalMotorhome(const FObjectInitializer& Init):Super(Init)
{CoolingSystem=CreateDefaultSubobject<URVCoolingComponent>(TEXT("CoolingSystem"));}
float ARVMechanicalMotorhome::GetMechanicalOutputScale()const{return CoolingSystem->Engine.OutputScale;}
bool ARVMechanicalMotorhome::CanOperateEngine()const{return !CoolingSystem->Engine.bShutdown;}
void ARVMechanicalMotorhome::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps)const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(ARVMechanicalMotorhome,EngineService);}
void ARVMechanicalMotorhome::BeginPlay()
{
    Super::BeginPlay();if(!HasAuthority())return;
    EngineService=GetWorld()->SpawnActorDeferred<ARVServicePoint>(ARVServicePoint::StaticClass(),GetActorTransform(),this);
    if(!EngineService)return;EngineService->Vehicle=this;EngineService->FinishSpawning(GetActorTransform());
    EngineService->AttachToComponent(GetMesh(),FAttachmentTransformRules::SnapToTargetNotIncludingScale);EngineService->SetActorRelativeLocation(EngineServiceLocation);
}
