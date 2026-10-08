#include "Player/RVCharacterPresentationComponent.h"
#include "Player/RVCharacterVisualProfile.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVPlayerState.h"
#include "Player/RVLadderClimbComponent.h"
#include "Survival/RVRestPoseComponent.h"
#include "Medical/RVHealthComponent.h"
#include "Vehicles/RVVehicleBase.h"
#include "Vehicles/RVVehicleSeatComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Camera/CameraComponent.h"
URVCharacterPresentationComponent::URVCharacterPresentationComponent()
{ PrimaryComponentTick.bCanEverTick=true; }
bool URVCharacterPresentationComponent::HasConfiguredVisuals() const
{ return Profile && Profile->Body && Profile->AnimationClass; }
void URVCharacterPresentationComponent::BeginPlay()
{
    Super::BeginPlay();auto* C=Cast<ARVSurvivorCharacter>(GetOwner());
    if(!C || !HasConfiguredVisuals()){SetComponentTickEnabled(false);return;}
    auto* Mesh=C->GetMesh();
    Mesh->SetSkeletalMesh(Profile->Body);Mesh->SetAnimInstanceClass(Profile->AnimationClass);
    Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);Mesh->SetSimulatePhysics(false);
    Mesh->SetOwnerNoSee(false);Mesh->SetHiddenInGame(false);Mesh->SetRelativeScale3D(Profile->Scale);
    if(auto* Camera=C->FindComponentByClass<UCameraComponent>()) Camera->AddLocalOffset(Profile->OwnerCameraOffset);
    Mesh->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
    Mesh->AddTickPrerequisiteComponent(this);
    TArray<USceneComponent*> Children;Mesh->GetChildrenComponents(true,Children);
    for(auto* Child:Children) if(auto* Primitive=Cast<UPrimitiveComponent>(Child)) Primitive->SetHiddenInGame(true);
    for(const auto& Spec:Profile->EquipmentAnchors)
    {
        if(Spec.Id.IsNone() || !Mesh->DoesSocketExist(Spec.Bone)) continue;
        auto* Anchor=NewObject<USceneComponent>(C);
        Anchor->SetupAttachment(Mesh,Spec.Bone);Anchor->SetRelativeTransform(Spec.Offset);Anchor->RegisterComponent();Anchors.Add(Spec.Id,Anchor);
    }
    bInitialized=true;RefreshVisualState();
}
void URVCharacterPresentationComponent::TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Function)
{ Super::TickComponent(Delta,Type,Function);RefreshVisualState(); }
void URVCharacterPresentationComponent::RefreshVisualState()
{
    auto* C=Cast<ARVSurvivorCharacter>(GetOwner());if(!C || !bInitialized) return;
    auto* Mesh=C->GetMesh();const auto* Rest=C->FindComponentByClass<URVRestPoseComponent>();
    const auto* Climb=C->FindComponentByClass<URVLadderClimbComponent>();
    const auto* Seat=Cast<URVVehicleSeatComponent>(C->GetRootComponent()->GetAttachParent());
    const auto* PS=C->GetPlayerState<ARVPlayerState>();
    if(!PS && C->SeatedVehicle && Seat && Seat->bDriverSeat && Seat->Occupant==C) PS=C->SeatedVehicle->GetPlayerState<ARVPlayerState>();
    if(Rest && Rest->RestPoint) VisualState=ERVCharacterVisualState::Bed;
    else if(PS && PS->Health && !PS->Health->CanAct()) VisualState=ERVCharacterVisualState::Downed;
    else if(C->SeatedVehicle && Seat) VisualState=Seat->bDriverSeat?ERVCharacterVisualState::Driver:ERVCharacterVisualState::Passenger;
    else if(Climb && Climb->Ladder) VisualState=ERVCharacterVisualState::Ladder;
    else if(PS && PS->Health && PS->Health->ActiveTreatment.IsValid()) VisualState=ERVCharacterVisualState::Treatment;
    else VisualState=ERVCharacterVisualState::Locomotion;
    // Discrete visual offsets only. Native mesh smoothing carries normal walking.
    const int32 DesiredPlacement=VisualState==ERVCharacterVisualState::Bed?1:(VisualState==ERVCharacterVisualState::Downed && !C->SeatedVehicle?2:(C->SeatedVehicle?3:0));
    if(DesiredPlacement!=Placement)
    {
        Placement=DesiredPlacement;
        FVector Offset=Profile->StandingOffset-FVector(0,0,C->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight());
        if(Placement==1) Offset=Profile->BedOffset;
        else if(Placement==2) Offset=Profile->DownedOffset-FVector(0,0,C->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight());
        else if(Placement==3) Offset+=Profile->SeatedOffset;
        const FRotator Rotation=Placement==1?Profile->BedMeshRotation:Profile->MeshRotation;
        Mesh->SetRelativeLocationAndRotation(Offset,Rotation);
        C->CacheInitialMeshOffset(Offset,Rotation);
    }
    const bool HideHead=C->IsLocallyControlled();
    if(HideHead!=bHeadHidden && !Profile->OwnerHiddenHead.IsNone())
    {
        bHeadHidden=HideHead;
        if(HideHead) Mesh->HideBoneByName(Profile->OwnerHiddenHead,EPhysBodyOp::PBO_None);
        else Mesh->UnHideBoneByName(Profile->OwnerHiddenHead);
    }
}
bool URVCharacterPresentationComponent::ResolveBodyRegion(FName Bone,ERVBodyRegion& Region) const
{
    if(!HasConfiguredVisuals()) return false;
    const auto& Skeleton=Profile->Body->GetRefSkeleton();int32 Index=Skeleton.FindBoneIndex(Bone);
    while(Index!=INDEX_NONE)
    {
        const FName Name=Skeleton.GetBoneName(Index);
        for(const auto& Binding:Profile->BodyRegions) if(Binding.Roots.Contains(Name)){Region=Binding.Region;return true;}
        Index=Skeleton.GetParentIndex(Index);
    }
    return false;
}
FTransform URVCharacterPresentationComponent::GetBodyRegionTransform(ERVBodyRegion Region) const
{
    const auto* C=Cast<ARVSurvivorCharacter>(GetOwner());
    if(C && Profile) for(const auto& Binding:Profile->BodyRegions) if(Binding.Region==Region) return C->GetMesh()->GetSocketTransform(Binding.AnchorBone);
    return GetOwner()->GetActorTransform();
}
USceneComponent* URVCharacterPresentationComponent::GetEquipmentAnchor(FName Id) const
{ const auto* Found=Anchors.Find(Id);return Found?Found->Get():nullptr; }
