#include "Vehicles/RVMechanicalMotorhome.h"
#include "Mechanical/RVCoolingComponent.h"
#include "Mechanical/RVServicePoint.h"
#include "Net/UnrealNetwork.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Vehicles/RVInteractiveDoor.h"
#include "Vehicles/RVEngineHood.h"
ARVMechanicalMotorhome::ARVMechanicalMotorhome(const FObjectInitializer& Init):Super(Init)
{CoolingSystem=CreateDefaultSubobject<URVCoolingComponent>(TEXT("CoolingSystem"));}
float ARVMechanicalMotorhome::GetMechanicalOutputScale()const{return EngineHood && EngineHood->bOpen?0:CoolingSystem->Engine.OutputScale;}
bool ARVMechanicalMotorhome::CanOperateEngine()const{return !CoolingSystem->Engine.bShutdown && (!EngineHood || !EngineHood->bOpen);}
void ARVMechanicalMotorhome::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps)const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(ARVMechanicalMotorhome,EngineService);DOREPLIFETIME(ARVMechanicalMotorhome,EngineHood);}
void ARVMechanicalMotorhome::BeginPlay()
{
    Super::BeginPlay();
    const auto* Hood=VisualParts.FindByPredicate([this](const FRVVisualPart& Part){return Part.Name==HoodPartName;});
    if(Hood)for(auto* Part:TInlineComponentArray<UStaticMeshComponent*>(this))if(Part->GetStaticMesh()==Hood->Mesh){Part->SetVisibility(false);Part->SetHiddenInGame(true);}
    if(!HasAuthority())return;
    if(Hood && Hood->Mesh)
    {
        EngineHood=GetWorld()->SpawnActorDeferred<ARVEngineHood>(ARVEngineHood::StaticClass(),GetActorTransform(),this);
        if(EngineHood)
        {
            EngineHood->DoorMesh=Hood->Mesh;EngineHood->DoorMaterials=Hood->Materials;EngineHood->bPitchHinge=true;EngineHood->OpenAngle=60;
            EngineHood->CollisionCenter=HoodCollisionCenter;EngineHood->CollisionExtent=HoodCollisionExtent;EngineHood->DoorLabel=FText::FromString(TEXT("Engine hood"));
            EngineHood->FinishSpawning(GetActorTransform());EngineHood->AttachToComponent(GetMesh(),FAttachmentTransformRules::SnapToTargetNotIncludingScale);EngineHood->SetActorRelativeLocation(Hood->Transform.GetLocation());
        }
    }
    EngineService=GetWorld()->SpawnActorDeferred<ARVServicePoint>(ARVServicePoint::StaticClass(),GetActorTransform(),this);
    if(!EngineService)return;EngineService->Vehicle=this;EngineService->FinishSpawning(GetActorTransform());
    EngineService->AttachToComponent(GetMesh(),FAttachmentTransformRules::SnapToTargetNotIncludingScale);EngineService->SetActorRelativeLocation(EngineServiceLocation);
}
