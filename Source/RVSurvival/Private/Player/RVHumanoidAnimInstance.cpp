#include "Player/RVHumanoidAnimInstance.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVCharacterPresentationComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Combat/RVInfected.h"
#include "Combat/RVCombatComponent.h"
void URVHumanoidAnimInstance::NativeUpdateAnimation(float Delta)
{
    Super::NativeUpdateAnimation(Delta);
    const auto* Character=Cast<ACharacter>(TryGetPawnOwner());
    if(!Character) return;
    const auto* Visual=Character->FindComponentByClass<URVCharacterPresentationComponent>();
    const auto* Movement=Character->GetCharacterMovement();
    const FVector Velocity=Movement->Velocity;
    GroundSpeed=Velocity.Size2D();
    Direction=GroundSpeed>1?FMath::RadiansToDegrees(FMath::Atan2(FVector::DotProduct(Velocity,Character->GetActorRightVector()),FVector::DotProduct(Velocity,Character->GetActorForwardVector()))):0;
    PoseIndex=Visual?int32(Visual->VisualState):0;
    const auto* Combat=Character->FindComponentByClass<URVCombatComponent>();bWeaponReady=Combat && Combat->bEnabled && Combat->EquippedWeapon.IsValid() && PoseIndex==0;
    AimPitch=FMath::Clamp(FRotator::NormalizeAxis(Character->GetBaseAimRotation().Pitch),-75.f,75.f);
    NormalizedAimPitch=AimPitch/90.f; // Epic AO_Pistol uses normalized -1..1 axes, not degrees.
    if(const auto* Survivor=Cast<ARVSurvivorCharacter>(Character);Survivor && PoseIndex==4 && Survivor->SeatedVehicle) PoseIndex=10;
    if(const auto* Infected=Cast<ARVInfected>(Character))PoseIndex=Infected->State==ERVInfectedState::Dead?4:Infected->State==ERVInfectedState::Attack?6:0;
    ClimbPlayRate=FMath::Clamp(Velocity.Z/100.f,-1.5f,1.5f);
    if(PoseIndex==0)
    {
        const bool Falling=Movement->IsFalling();
        if(bWasFalling && !Falling) LandingRemaining=.18f;
        LandingRemaining=FMath::Max(0.f,LandingRemaining-Delta);
        if(Falling) PoseIndex=Velocity.Z>30?8:7;
        else if(LandingRemaining>0) PoseIndex=9;
        bWasFalling=Falling;
    }
    else { bWasFalling=false;LandingRemaining=0; }
}

