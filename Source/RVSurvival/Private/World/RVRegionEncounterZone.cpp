#include "World/RVRegionEncounterZone.h"
#include "World/RVEncounterDirector.h"
#include "World/RVScavengeContainer.h"
#include "Combat/RVInfected.h"
#include "Combat/RVInfectedProfile.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"
#include "NavigationSystem.h"
#include "TimerManager.h"
#include "Net/UnrealNetwork.h"
ARVRegionEncounterZone::ARVRegionEncounterZone()
{
 SetRootComponent(CreateDefaultSubobject<USceneComponent>(TEXT("ContextAnchor")));
 bReplicates=true;bAlwaysRelevant=false;SetNetCullDistanceSquared(FMath::Square(22000.f));
#if WITH_EDITOR
 SetIsSpatiallyLoaded(false); // Five/small authored directors stay loaded; spawned populations remain bounded.
#endif
}
void ARVRegionEncounterZone::BeginPlay()
{
 Super::BeginPlay();if(!HasAuthority())return;
 auto* Director=GetWorld()->GetSubsystem<URVEncounterDirector>();bOwnsIdentity=Director && Director->Claim(ZoneId,this);
 if(!bOwnsIdentity){UE_LOG(LogTemp,Error,TEXT("Region encounter zone %s needs a unique authored GUID"),*GetName());return;}
 GetWorldTimerManager().SetTimer(UpdateTimer,this,&ThisClass::UpdateAuthority,2.f,true);
}
bool ARVRegionEncounterZone::IsSafeSpawn(const FVector& Position,float Radius,float HalfHeight) const
{
 if(!Profile || GetWorld()->OverlapBlockingTestByChannel(Position,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(Radius,HalfHeight)))return false;
 for(auto It=GetWorld()->GetPlayerControllerIterator();It;++It)
 {
  auto* PC=It->Get();if(!PC || !PC->GetPawn())continue;
  if(FVector::DistSquared(Position,PC->GetPawn()->GetActorLocation())<FMath::Square(FMath::Max(Profile->MinimumSpawnDistance,500.f)))return false;
  FVector Eye;FRotator View;PC->GetPlayerViewPoint(Eye,View);
  if(FVector::DotProduct((Position-Eye).GetSafeNormal(),View.Vector())>.25f)
  {
   FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(RVEncounterVisibility),false,PC->GetPawn());
   if(!GetWorld()->LineTraceSingleByChannel(Hit,Eye,Position,ECC_Visibility,Params))return false;
  }
 }
 return true;
}
void ARVRegionEncounterZone::UpdateAuthority()
{
 if(!HasAuthority() || !bOwnsIdentity || !Profile)return;
 auto* Director=GetWorld()->GetSubsystem<URVEncounterDirector>();if(!Director)return;
 double DistanceSquared=DBL_MAX;
 for(auto It=GetWorld()->GetPlayerControllerIterator();It;++It)
  if(auto* PC=It->Get();PC && PC->GetPawn())DistanceSquared=FMath::Min(DistanceSquared,FVector::DistSquared(GetActorLocation(),PC->GetPawn()->GetActorLocation()));
 const float ActiveRadius=FMath::Clamp(Profile->ActiveRadius,5000.f,25000.f);
 const float ReleaseRadius=FMath::Max(ActiveRadius+2000,FMath::Clamp(Profile->ReleaseRadius,7000.f,35000.f));
 if(DistanceSquared>FMath::Square(ReleaseRadius))
 {
  bool Engaged=false;
  for(const auto& Pair:Members)if(auto* Actor=Pair.Value.Get();Actor && Actor->State!=ERVInfectedState::Dead)
   for(auto It=GetWorld()->GetPlayerControllerIterator();It;++It)
    if(auto* PC=It->Get();PC && PC->GetPawn() && FVector::DistSquared(Actor->GetActorLocation(),PC->GetPawn()->GetActorLocation())<FMath::Square(5000.f))Engaged=true;
  if(!Engaged){if(bActive)SuspendAuthority();return;}
 }
 if(!bActive && DistanceSquared>FMath::Square(ActiveRadius))return;
 TArray<FVector> Positions;for(const auto& Offset:SpawnOffsets)Positions.Add(GetActorTransform().TransformPosition(Offset));
 auto& Record=Director->SelectAuthority(ZoneId,Profile,Positions);Outcome=Record.Outcome;bEvaluated=true;bActive=true;ForceNetUpdate();
 if(Outcome==ERVEncounterOutcome::SupplyCache && !Cache.IsValid() && SupplyCacheClass && Profile->SupplyProfile && Positions.Num()>0)
 {
  FHitResult Ground;FCollisionQueryParams Params(SCENE_QUERY_STAT(RVCacheGround),false,this);
  if(GetWorld()->LineTraceSingleByChannel(Ground,Positions[0]+FVector(0,0,2000),Positions[0]-FVector(0,0,2000),ECC_Visibility,Params))
  {
   const FVector Location=Ground.ImpactPoint+FVector(0,0,40);
   if(!GetWorld()->OverlapBlockingTestByChannel(Location,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeBox(FVector(60,40,39))) && IsSafeSpawn(Location,30,35))
   {
    auto* Supply=GetWorld()->SpawnActorDeferred<ARVScavengeContainer>(SupplyCacheClass,FTransform(Location));
    if(Supply){Supply->ContainerId=FGuid(ZoneId.A^0xA70C164D,ZoneId.B,ZoneId.C,ZoneId.D);Supply->LootProfile=Profile->SupplyProfile;Supply->FinishSpawning(FTransform(Location));Cache=Supply;}
   }
  }
 }
 if(Outcome!=ERVEncounterOutcome::InfectedCluster)return;
 auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld());if(!Nav)return;
 const auto* Defaults=GetDefault<ARVInfected>();const float Radius=Defaults->GetCapsuleComponent()->GetUnscaledCapsuleRadius(),Half=Defaults->GetCapsuleComponent()->GetUnscaledCapsuleHalfHeight();
 for(int32 Index=0;Index<Record.Infected.Num();++Index)
 {
  auto& Snapshot=Record.Infected[Index];if(Snapshot.bDead)continue;
  if(auto* Existing=Members.Find(Index))
  {
   if(auto* Actor=Existing->Get())
   {if(Actor->State==ERVInfectedState::Dead){Snapshot.bDead=true;Actor->Destroy();Members.Remove(Index);}continue;}
   // An externally destroyed active member is exhausted, never silently respawned.
   Snapshot.bDead=true;Members.Remove(Index);continue;
  }
  if(Director->ActiveCount()>=FMath::Clamp(Director->MaximumActiveInfected,1,16))break;
  FNavLocation Floor;if(!Nav->ProjectPointToNavigation(Snapshot.Position,Floor,FVector(300,300,2500)))continue;
  const FVector Spawn=Floor.Location+FVector(0,0,Half+3);if(!IsSafeSpawn(Spawn,Radius,Half))continue;
  auto* Infected=GetWorld()->SpawnActorDeferred<ARVInfected>(ARVInfected::StaticClass(),FTransform(Spawn));
  if(!Infected)continue;
  Infected->Profile=Profile->InfectedProfile;Infected->FinishSpawning(FTransform(Spawn));Infected->Vitality=Snapshot.Vitality;Infected->bLegInjured=Snapshot.bLegInjured;
  if(Snapshot.bLegInjured)Infected->GetCharacterMovement()->MaxWalkSpeed=Infected->Tuning()->ChaseSpeed*.5f;
  Infected->SetNetCullDistanceSquared(FMath::Square(20000.f));Members.Add(Index,Infected);Director->ActiveInfected.Add(Infected);
 }
}
void ARVRegionEncounterZone::SuspendAuthority()
{
 if(auto* Director=GetWorld()->GetSubsystem<URVEncounterDirector>())
  if(auto* Record=Director->Encounters.Find(ZoneId))
   for(const auto& Pair:Members)
    if(Record->Infected.IsValidIndex(Pair.Key))
    {
     auto& Snapshot=Record->Infected[Pair.Key];
     if(auto* Actor=Pair.Value.Get()){Snapshot.Position=Actor->GetActorLocation();Snapshot.Vitality=Actor->Vitality;Snapshot.bDead=Actor->State==ERVInfectedState::Dead;Snapshot.bLegInjured=Actor->bLegInjured;Actor->Destroy();}
     else Snapshot.bDead=true;
    }
 Members.Empty();if(Cache.IsValid())Cache->Destroy();Cache.Reset();bActive=false;
}
void ARVRegionEncounterZone::EndPlay(const EEndPlayReason::Type Reason)
{
 GetWorldTimerManager().ClearTimer(UpdateTimer);
 if(HasAuthority() && bOwnsIdentity){SuspendAuthority();if(auto* Director=GetWorld()->GetSubsystem<URVEncounterDirector>())Director->Release(ZoneId,this);}
 Super::EndPlay(Reason);
}
void ARVRegionEncounterZone::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(ARVRegionEncounterZone,Outcome);DOREPLIFETIME(ARVRegionEncounterZone,bEvaluated);}
