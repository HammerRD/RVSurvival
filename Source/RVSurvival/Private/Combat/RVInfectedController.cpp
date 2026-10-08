#include "Combat/RVInfectedController.h"
#include "Combat/RVInfected.h"
#include "Combat/RVInfectedProfile.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVPlayerState.h"
#include "Medical/RVHealthComponent.h"
#include "Perception/AIPerceptionComponent.h"
#include "Perception/AISenseConfig_Sight.h"
#include "Perception/AISenseConfig_Hearing.h"
#include "Perception/AISense_Sight.h"
#include "Perception/AISense_Hearing.h"
#include "BehaviorTree/BehaviorTree.h"
#include "BehaviorTree/BehaviorTreeComponent.h"
#include "BehaviorTree/Composites/BTComposite_Sequence.h"
#include "NavigationSystem.h"
#include "BrainComponent.h"
#include "Navigation/PathFollowingComponent.h"
ARVInfectedController::ARVInfectedController()
{
    Senses=CreateDefaultSubobject<UAIPerceptionComponent>(TEXT("Senses"));SetPerceptionComponent(*Senses);
    Sight=CreateDefaultSubobject<UAISenseConfig_Sight>(TEXT("Sight"));Hearing=CreateDefaultSubobject<UAISenseConfig_Hearing>(TEXT("Hearing"));
    Sight->DetectionByAffiliation.bDetectEnemies=Sight->DetectionByAffiliation.bDetectFriendlies=Sight->DetectionByAffiliation.bDetectNeutrals=true;
    Hearing->DetectionByAffiliation.bDetectEnemies=Hearing->DetectionByAffiliation.bDetectFriendlies=Hearing->DetectionByAffiliation.bDetectNeutrals=true;
    Senses->ConfigureSense(*Sight);Senses->ConfigureSense(*Hearing);
}
void ARVInfectedController::OnPossess(APawn* PossessedPawn)
{
    Super::OnPossess(PossessedPawn);auto* I=Cast<ARVInfected>(PossessedPawn);if(!I || !HasAuthority())return;const auto* P=I->Tuning();Home=PossessedPawn->GetActorLocation();
    Sight->SightRadius=P->SightRadius;Sight->LoseSightRadius=P->SightRadius+200;Sight->PeripheralVisionAngleDegrees=P->SightAngle;Sight->SetMaxAge(5);
    Hearing->HearingRange=P->HearingRadius;Hearing->SetMaxAge(5);
    Senses->ConfigureSense(*Sight);Senses->ConfigureSense(*Hearing);Senses->SetDominantSense(UAISense_Sight::StaticClass());Senses->OnTargetPerceptionUpdated.AddDynamic(this,&ThisClass::PerceptionChanged);
    // Engine-owned BT execution/path following. Single task is intentionally small;
    // later variants can provide asset-authored subtrees without changing perception.
    Behavior=NewObject<UBehaviorTree>(this);auto* Root=NewObject<UBTComposite_Sequence>(Behavior);Behavior->RootNode=Root;
    FBTCompositeChild Child;Child.ChildTask=NewObject<URVBTTask_Infected>(Behavior);Root->Children.Add(Child);RunBehaviorTree(Behavior);
}
void ARVInfectedController::PerceptionChanged(AActor* Actor,FAIStimulus Stimulus)
{
    if(Stimulus.Type==UAISense::GetSenseID<UAISense_Sight>())
    {if(!Cast<ARVSurvivorCharacter>(Actor))return;
     if(Stimulus.WasSuccessfullySensed()){VisibleTarget=Actor;LastKnown=Stimulus.StimulusLocation;}
     else if(VisibleTarget==Actor){VisibleTarget.Reset();InvestigateUntil=GetWorld()->GetTimeSeconds()+6;}}
    else if(Stimulus.WasSuccessfullySensed() && !VisibleTarget.IsValid())
    {LastKnown=Stimulus.StimulusLocation;InvestigateUntil=GetWorld()->GetTimeSeconds()+6;}
}
void ARVInfectedController::UpdateBehavior()
{
    auto* I=Cast<ARVInfected>(GetPawn());if(!I || I->State==ERVInfectedState::Dead)return;const auto* P=I->Tuning();
    auto* V=Cast<ARVSurvivorCharacter>(VisibleTarget.Get());
    if(V){const auto* PS=V->GetPlayerState<ARVPlayerState>();if(!PS || !PS->Health->CanAct()){VisibleTarget.Reset();V=nullptr;}}
    if(V)
    {LastKnown=V->GetActorLocation();if(FVector::DistSquared(I->GetActorLocation(),LastKnown)<=FMath::Square(P->AttackRange*.9f))
     {StopMovement();SetFocus(V);I->BeginAttack(V);}else{ClearFocus(EAIFocusPriority::Gameplay);I->State=ERVInfectedState::Chase;
      // Native reach tests add collision radii. StopOnOverlap previously stopped
      // outside melee reach; keep the goal clearance without adding our radius.
      MoveToActor(V,P->AttackRange*.5f,false,true,true,nullptr,true);}return;}
    ClearFocus(EAIFocusPriority::Gameplay);const double Now=GetWorld()->GetTimeSeconds();
    if(Now<InvestigateUntil){I->State=ERVInfectedState::Investigate;MoveToLocation(LastKnown,60,true,true,false,true);return;}
    if(Now>=NextWander){NextWander=Now+5;FNavLocation Point;if(auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld());Nav && Nav->GetRandomReachablePointInRadius(Home,P->WanderRadius,Point))
      {I->State=ERVInfectedState::Wander;MoveToLocation(Point.Location,45,true,true,false,true);}else I->State=ERVInfectedState::Idle;}
    else if(GetMoveStatus()==EPathFollowingStatus::Idle)I->State=ERVInfectedState::Idle;
}
void ARVInfectedController::EndPlay(const EEndPlayReason::Type Reason)
{Senses->OnTargetPerceptionUpdated.RemoveDynamic(this,&ThisClass::PerceptionChanged);VisibleTarget.Reset();Super::EndPlay(Reason);}
URVBTTask_Infected::URVBTTask_Infected(){NodeName=TEXT("Infected survival behavior");bNotifyTick=true;bTickIntervals=true;}
EBTNodeResult::Type URVBTTask_Infected::ExecuteTask(UBehaviorTreeComponent& Owner,uint8* Memory)
{if(auto* AI=Cast<ARVInfectedController>(Owner.GetAIOwner())){AI->UpdateBehavior();SetNextTickTime(Memory,.2f);return EBTNodeResult::InProgress;}return EBTNodeResult::Failed;}
void URVBTTask_Infected::TickTask(UBehaviorTreeComponent& Owner,uint8* Memory,float Delta)
{if(auto* AI=Cast<ARVInfectedController>(Owner.GetAIOwner()))AI->UpdateBehavior();SetNextTickTime(Memory,.2f);}
