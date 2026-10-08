#include "Combat/RVInfected.h"
#include "Combat/RVInfectedProfile.h"
#include "Combat/RVInfectedController.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVPlayerState.h"
#include "Player/RVCharacterVisualProfile.h"
#include "Medical/RVHealthComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/DamageEvents.h"
#include "Net/UnrealNetwork.h"
#include "TimerManager.h"
#include "Kismet/GameplayStatics.h"
#include "BrainComponent.h"
ARVInfected::ARVInfected()
{bReplicates=true;AIControllerClass=ARVInfectedController::StaticClass();AutoPossessAI=EAutoPossessAI::PlacedInWorldOrSpawned;
 bUseControllerRotationYaw=false;GetCharacterMovement()->bOrientRotationToMovement=true;
 GetMesh()->SetRelativeLocation(FVector(0,0,-88));GetMesh()->SetRelativeRotation(FRotator(0,-90,0));}
const URVInfectedProfile* ARVInfected::Tuning() const{return Profile?Profile.Get():GetDefault<URVInfectedProfile>();}
void ARVInfected::ConfigureVisual()
{const auto* P=Tuning();if(P->Body)GetMesh()->SetSkeletalMesh(P->Body);if(P->AnimationClass)GetMesh()->SetAnimInstanceClass(P->AnimationClass);
 if(P->BodyMaterial)for(int32 Index=0;Index<GetMesh()->GetNumMaterials();++Index)GetMesh()->SetMaterial(Index,P->BodyMaterial);}
void ARVInfected::OnConstruction(const FTransform& Transform){Super::OnConstruction(Transform);ConfigureVisual();}
void ARVInfected::BeginPlay()
{Super::BeginPlay();const auto* P=Tuning();if(HasAuthority())Vitality=P->Vitality;
 GetCharacterMovement()->MaxWalkSpeed=P->ChaseSpeed;
 ConfigureVisual();
 GetMesh()->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
 GetMesh()->SetCollisionEnabled(ECollisionEnabled::QueryOnly);GetMesh()->SetCollisionResponseToAllChannels(ECR_Ignore);
 GetMesh()->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility,ECR_Ignore);}
void ARVInfected::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(ARVInfected,State);DOREPLIFETIME(ARVInfected,Vitality);DOREPLIFETIME(ARVInfected,bLegInjured);DOREPLIFETIME(ARVInfected,AttackSequence);DOREPLIFETIME(ARVInfected,DeathSequence);}
float ARVInfected::TakeDamage(float Amount,const FDamageEvent& Event,AController* DamageInstigator,AActor* Causer)
{
    if(!HasAuthority() || State==ERVInfectedState::Dead || !FMath::IsFinite(Amount) || Amount<=0)return 0;
    ERVBodyRegion Region=ERVBodyRegion::Torso;const auto* P=Tuning();
    if(Event.IsOfType(FPointDamageEvent::ClassID) && P->BodyMapping)
    {const FName Bone=static_cast<const FPointDamageEvent&>(Event).HitInfo.BoneName;
     FName Current=Bone;while(!Current.IsNone())
     {bool Found=false;for(const auto& R:P->BodyMapping->BodyRegions)if(R.Roots.Contains(Current) || R.AnchorBone==Current){Region=R.Region;Found=true;break;}
      if(Found)break;const int32 Index=GetMesh()->GetBoneIndex(Current);if(Index==INDEX_NONE)break;Current=GetMesh()->GetParentBone(Current);}}
    const bool Limb=Region==ERVBodyRegion::LeftArm || Region==ERVBodyRegion::RightArm || Region==ERVBodyRegion::LeftLeg || Region==ERVBodyRegion::RightLeg;
    const float Applied=Amount*(Region==ERVBodyRegion::Head?P->HeadMultiplier:Limb?P->LimbMultiplier:1.f);
    Vitality=FMath::Max(0.f,Vitality-Applied);
    if(Region==ERVBodyRegion::LeftLeg || Region==ERVBodyRegion::RightLeg){bLegInjured=true;GetCharacterMovement()->MaxWalkSpeed=P->ChaseSpeed*.5f;}
    if(Vitality<=0){State=ERVInfectedState::Dead;++DeathSequence;GetWorld()->GetTimerManager().ClearTimer(AttackTimer);AttackVictim.Reset();
        if(auto* AI=Cast<AAIController>(Controller)){AI->StopMovement();if(AI->BrainComponent)AI->BrainComponent->StopLogic(TEXT("Dead"));}OnRep_State();}
    ForceNetUpdate();return Applied;
}
void ARVInfected::BeginAttack(AActor* Victim)
{
    if(!HasAuthority() || State==ERVInfectedState::Dead || GetWorld()->GetTimeSeconds()<NextAttack || GetWorld()->GetTimerManager().IsTimerActive(AttackTimer))return;
    const auto* P=Tuning();AttackVictim=Victim;State=ERVInfectedState::Attack;++AttackSequence;
    NextAttack=GetWorld()->GetTimeSeconds()+FMath::Max(P->AttackCooldown,P->AttackWindup+.1f);
    GetWorld()->GetTimerManager().SetTimer(AttackTimer,this,&ThisClass::CompleteAttack,FMath::Max(.1f,P->AttackWindup),false);ForceNetUpdate();
}
void ARVInfected::CompleteAttack()
{
    auto* V=Cast<ARVSurvivorCharacter>(AttackVictim.Get());const auto* P=Tuning();
    if(State==ERVInfectedState::Dead || !V || FVector::DistSquared(GetActorLocation(),V->GetActorLocation())>FMath::Square(P->AttackRange))return;
    auto* PS=V->GetPlayerState<ARVPlayerState>();if(!PS || !PS->Health->CanAct())return;
    FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(RVInfectedAttack),false,this);
    const FVector Start=GetActorLocation()+FVector(0,0,35),End=V->GetActorLocation()+FVector(0,0,35);
    if(GetWorld()->LineTraceSingleByChannel(Hit,Start,End,ECC_Visibility,Params) && Hit.GetActor()!=V)return;
    UGameplayStatics::ApplyPointDamage(V,P->AttackDamage,(End-Start).GetSafeNormal(),Hit,Controller,this,nullptr);
    AttackVictim.Reset();
}
void ARVInfected::OnRep_State()
{if(State==ERVInfectedState::Dead){GetCharacterMovement()->StopMovementImmediately();GetCharacterMovement()->DisableMovement();
 if(Tuning()->BodyMapping){GetMesh()->SetRelativeLocation(Tuning()->BodyMapping->DownedOffset-FVector(0,0,GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight()));}
 GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);}}
void ARVInfected::EndPlay(const EEndPlayReason::Type Reason)
{GetWorld()->GetTimerManager().ClearTimer(AttackTimer);AttackVictim.Reset();Super::EndPlay(Reason);}
