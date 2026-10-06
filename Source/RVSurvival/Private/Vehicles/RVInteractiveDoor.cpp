#include "Vehicles/RVInteractiveDoor.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/Pawn.h"
#include "Net/UnrealNetwork.h"
ARVInteractiveDoor::ARVInteractiveDoor()
{
    bReplicates=true; bAlwaysRelevant=true; SetReplicateMovement(true);
    SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("DoorMount")));
    Hinge=CreateDefaultSubobject<USceneComponent>(TEXT("Hinge")); Hinge->SetupAttachment(GetRootComponent());
    Visual=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VendorDoorVisual")); Visual->SetupAttachment(Hinge); Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Glass=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("VendorGlassVisual")); Glass->SetupAttachment(Hinge); Glass->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    DoorCollision=CreateDefaultSubobject<UBoxComponent>(TEXT("DoorCollision")); DoorCollision->SetupAttachment(Hinge);
    DoorCollision->SetCollisionEnabled(ECollisionEnabled::QueryOnly); DoorCollision->SetCollisionResponseToAllChannels(ECR_Block);
    DoorCollision->SetCollisionResponseToChannel(ECC_PhysicsBody,ECR_Ignore); DoorCollision->SetMobility(EComponentMobility::Movable);
    DoorLabel=FText::FromString(TEXT("RV house door"));
}
void ARVInteractiveDoor::BeginPlay() { Super::BeginPlay(); OnRep_Door(); }
void ARVInteractiveDoor::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(ARVInteractiveDoor,bOpen); DOREPLIFETIME(ARVInteractiveDoor,OpenAngle);
    DOREPLIFETIME(ARVInteractiveDoor,DoorMesh); DOREPLIFETIME(ARVInteractiveDoor,GlassMesh);
    DOREPLIFETIME(ARVInteractiveDoor,DoorMaterials); DOREPLIFETIME(ARVInteractiveDoor,GlassMaterials);
    DOREPLIFETIME(ARVInteractiveDoor,GlassOffset); DOREPLIFETIME(ARVInteractiveDoor,CollisionCenter);
    DOREPLIFETIME(ARVInteractiveDoor,CollisionExtent); DOREPLIFETIME(ARVInteractiveDoor,DoorLabel);
}
void ARVInteractiveDoor::OnRep_Door()
{
    Visual->SetStaticMesh(DoorMesh); Glass->SetStaticMesh(GlassMesh); Glass->SetRelativeLocation(GlassOffset);
    for (int32 Index=0;Index<DoorMaterials.Num();++Index) if (DoorMaterials[Index]) Visual->SetMaterial(Index,DoorMaterials[Index]);
    for (int32 Index=0;Index<GlassMaterials.Num();++Index) if (GlassMaterials[Index]) Glass->SetMaterial(Index,GlassMaterials[Index]);
    Glass->bDisallowNanite=true; // Preserve the accepted project-side translucent glass policy.
    DoorCollision->SetRelativeLocation(CollisionCenter); DoorCollision->SetBoxExtent(CollisionExtent);
    Hinge->SetRelativeRotation(FRotator(0,bOpen?OpenAngle:0,0));
}
bool ARVInteractiveDoor::IsSwingClear(bool ToOpen) const
{
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RVDoorSwing),false,this);
    // Check the full sampled swing, including the destination, against actual player capsules.
    for (int32 Step=0;Step<=18;++Step)
    {
        const float Angle=FMath::Lerp(bOpen?OpenAngle:0.f,ToOpen?OpenAngle:0.f,Step/18.f);
        const FQuat Rotation=GetActorQuat()*FRotator(0,Angle,0).Quaternion();
        const FVector Center=GetActorLocation()+Rotation.RotateVector(CollisionCenter);
        if (GetWorld()->OverlapAnyTestByObjectType(Center,Rotation,FCollisionObjectQueryParams(ECC_Pawn),
            FCollisionShape::MakeBox(CollisionExtent+FVector(2)),Params)) return false;
    }
    return true;
}
bool ARVInteractiveDoor::CanInteract_Implementation(APawn* Pawn) const
{ return IsValid(Pawn) && Pawn->GetController(); }
FText ARVInteractiveDoor::GetInteractionText_Implementation(APawn*) const
{
    return FText::FromString(DoorLabel.ToString()+(IsSwingClear(!bOpen)?(bOpen?TEXT(" | Hold E: close"):TEXT(" | Hold E: open")):TEXT(" | Door swing obstructed; move clear")));
}
void ARVInteractiveDoor::CompleteInteraction_Implementation(APawn* Pawn)
{
    if (!HasAuthority() || !CanInteract_Implementation(Pawn) || !IsSwingClear(!bOpen)) return;
    bOpen=!bOpen; OnRep_Door(); ForceNetUpdate();
}
