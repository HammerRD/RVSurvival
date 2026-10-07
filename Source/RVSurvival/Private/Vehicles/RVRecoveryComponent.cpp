#include "Vehicles/RVRecoveryComponent.h"
#include "Vehicles/RVMechanicalMotorhome.h"
#include "Vehicles/RVVehicleSeatComponent.h"
#include "Vehicles/RVLadder.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Player/RVPlayerController.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVPlayerState.h"
#include "Player/RVPassengerReferenceFrameComponent.h"
#include "Player/RVLadderClimbComponent.h"
#include "Survival/RVNeedsComponent.h"
#include "Survival/RVRestPoseComponent.h"
#include "Interaction/RVInteractionComponent.h"
#include "Resources/RVElectricalComponent.h"
#include "Mechanical/RVServicePoint.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/GameStateBase.h"
#include "EngineUtils.h"
#include "Net/UnrealNetwork.h"
URVRecoveryComponent::URVRecoveryComponent(){SetIsReplicatedByDefault(true);PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.TickInterval=.1f;}
bool URVRecoveryComponent::IsPrototypeRecoveryAvailable()const
{
#if UE_BUILD_SHIPPING || UE_BUILD_TEST
 return false; // Shipping recovery must supply an equipment/cost policy.
#else
 return bPrototypeRecoveryEnabled;
#endif
}
void URVRecoveryComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps)const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(URVRecoveryComponent,bConfirmedOverturned);DOREPLIFETIME(URVRecoveryComponent,RecoveryRevision);DOREPLIFETIME(URVRecoveryComponent,RecoveryGraceUntil);}
bool URVRecoveryComponent::StopsPropulsion()const
{
 const auto* GS=GetWorld()?GetWorld()->GetGameState():nullptr;
 const double Now=GS?GS->GetServerWorldTimeSeconds():0;
 return bConfirmedOverturned || Now<RecoveryGraceUntil;
}
void URVRecoveryComponent::TickComponent(float DT,ELevelTick Type,FActorComponentTickFunction* Function)
{
 Super::TickComponent(DT,Type,Function);auto* RV=Cast<ARVMechanicalMotorhome>(GetOwner());if(!RV || !RV->HasAuthority())return;
 RV->SetAuthorityDriveLock(RV,GetWorld()->GetTimeSeconds()<RecoveryGraceUntil);
 const bool Overturned=FVector::DotProduct(RV->GetActorUpVector(),FVector::UpVector)<MaximumUpDot;
 const bool Still=RV->GetVelocity().Size()<=MaximumSpeed && RV->GetMesh()->GetPhysicsAngularVelocityInDegrees().Size()<=MaximumAngularSpeedDegrees;
 StableTime=Overturned && Still?StableTime+DT:0;
 const bool Ready=StableTime>=ConfirmationSeconds;
 if(Ready!=bConfirmedOverturned){bConfirmedOverturned=Ready;RV->ForceNetUpdate();}
}
bool URVRecoveryComponent::RecoverAuthority(ARVPlayerController* PC,FString& Feedback)
{
 auto Fail=[&](const TCHAR* Why){Feedback=Why;return false;};
 auto* RV=Cast<ARVMechanicalMotorhome>(GetOwner());
 if(!RV || !RV->HasAuthority() || !PC || !PC->GetPawn())return Fail(TEXT("Recovery requires server authority and an active player"));
 if(!IsPrototypeRecoveryAvailable())return Fail(TEXT("Recovery equipment is required"));
 if(!bConfirmedOverturned || RV->GetActorUpVector().Z>=MaximumUpDot)return Fail(TEXT("RV is not confirmed overturned"));
 if(RV->GetVelocity().Size()>MaximumSpeed || RV->GetMesh()->GetPhysicsAngularVelocityInDegrees().Size()>MaximumAngularSpeedDegrees)return Fail(TEXT("Wait until the RV stops moving"));
 if(PC->SeatedVehicle!=RV && FVector::Dist(PC->GetPawn()->GetActorLocation(),RV->GetActorLocation())>RequestRange)return Fail(TEXT("Move closer to the overturned RV"));
 if(RV->Electrical->bEngineRunning)return Fail(TEXT("Wait for engine shutdown"));
 if(RV->EngineService && RV->EngineService->RepairPlayer)return Fail(TEXT("Cancel the active repair first"));
 TArray<ARVSurvivorCharacter*> Seated,Evacuate;
 for(auto* Seat:RV->GetSeats())if(Seat->Occupant)
 {
  if(!Seat->OccupantController.IsValid() || GetWorld()->GetTimeSeconds()-Seat->OccupantController->SeatEntryTime<2)return Fail(TEXT("Wait for the seat transition to finish"));
  if(Seat->Occupant->GetInteraction()->HasActiveInteraction())return Fail(TEXT("Release interaction before recovery"));
  Seated.Add(Seat->Occupant);
 }
 const FBox Interior(FVector(-420,-160,20),FVector(440,160,370));
 for(TActorIterator<ARVSurvivorCharacter> It(GetWorld());It;++It)
 {
  auto* C=*It;auto* Frame=C->FindComponentByClass<URVPassengerReferenceFrameComponent>();
  auto* Climb=C->FindComponentByClass<URVLadderClimbComponent>();
  if((Climb->Ladder && Climb->Ladder->GetAttachParentActor()==RV) || (Climb->RoofLadder && Climb->RoofLadder->GetAttachParentActor()==RV))return Fail(TEXT("Leave the RV ladder and roof before recovery"));
  if(Seated.Contains(C) || (Frame->ReferenceFrame!=RV && !Interior.IsInside(RV->GetActorTransform().InverseTransformPosition(C->GetActorLocation()))))continue;
  if(!C->GetController())return Fail(TEXT("Passenger state is not ready"));
  auto* Ladder=C->FindComponentByClass<URVLadderClimbComponent>();
  if(Ladder->Ladder || Ladder->RoofLadder || C->FindComponentByClass<URVInteractionComponent>()->HasActiveInteraction())return Fail(TEXT("Leave the ladder or release interaction before recovery"));
  Evacuate.Add(C);
 }
 FCollisionQueryParams Params(SCENE_QUERY_STAT(RVRecoveryPlacement),false,RV);
 TArray<AActor*> Attached;RV->GetAttachedActors(Attached,true,true);Params.AddIgnoredActors(Attached);
 auto SupportedGround=[](const FHitResult& Hit)
 {
  if(Hit.ImpactNormal.Z<.9)return false;
  // A pawn or its attached geometry is not stable terrain for recovery.
  for(auto* Actor=Hit.GetActor();Actor;Actor=Actor->GetAttachParentActor())if(Actor->IsA<APawn>())return false;
  return true;
 };
 for(auto* C:Seated)Params.AddIgnoredActor(C);for(auto* C:Evacuate)Params.AddIgnoredActor(C);
 const FQuat Upright=FRotator(0,RV->GetActorRotation().Yaw,0).Quaternion();
 FVector Chosen=FVector::ZeroVector;TArray<FVector> SafePassengers;bool Found=false;
 const FVector Offsets[]={FVector::ZeroVector,FVector(150,0,0),FVector(-150,0,0),FVector(0,150,0),FVector(0,-150,0),FVector(300,0,0),FVector(-300,0,0),FVector(0,300,0),FVector(0,-300,0)};
 for(const auto& Offset:Offsets)
 {
  FVector Target=RV->GetActorLocation()+Offset;double Low=BIG_NUMBER,High=-BIG_NUMBER;bool Supported=true;
  for(FVector Foot:{FVector::ZeroVector,FVector(340,105,0),FVector(340,-105,0),FVector(-340,105,0),FVector(-340,-105,0)})
  {
   FVector P=Target+Upright.RotateVector(Foot);FHitResult Hit;
   if(!GetWorld()->LineTraceSingleByChannel(Hit,P+FVector(0,0,600),P-FVector(0,0,1000),ECC_Visibility,Params) || !SupportedGround(Hit)){Supported=false;break;}
   Low=FMath::Min(Low,double(Hit.ImpactPoint.Z));High=FMath::Max(High,double(Hit.ImpactPoint.Z));
  }
  if(!Supported || High-Low>45)continue;
  Target.Z=High+GroundClearance;const FVector Center=Target+Upright.RotateVector(PlacementCenter);
  if(FMath::Abs(Target.Z-RV->GetActorLocation().Z)>MaximumVerticalShift)continue;
  if(GetWorld()->OverlapAnyTestByObjectType(Center,Upright,FCollisionObjectQueryParams::AllObjects,FCollisionShape::MakeBox(PlacementExtent),Params))continue;
  SafePassengers.Reset();
  for(auto* C:Evacuate)
  {
   bool Safe=false;const float Radius=FMath::Max(C->GetCapsuleComponent()->GetScaledCapsuleRadius(),C->FindComponentByClass<URVPassengerReferenceFrameComponent>()->GetOutsideCapsuleRadius());
   const float Half=C->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
   for(int32 i=0;i<16;++i)
   {
    const float Angle=i*PI/8;FVector P=Target+FVector(FMath::Cos(Angle)*650,FMath::Sin(Angle)*650,0);FHitResult Hit;
    if(!GetWorld()->LineTraceSingleByChannel(Hit,P+FVector(0,0,400),P-FVector(0,0,800),ECC_Visibility,Params) || !SupportedGround(Hit))continue;
    P=Hit.ImpactPoint+FVector(0,0,Half+3);
    if(GetWorld()->OverlapAnyTestByObjectType(P,FQuat::Identity,FCollisionObjectQueryParams::AllObjects,FCollisionShape::MakeCapsule(Radius,Half),Params))continue;
    if(FBox(PlacementCenter-PlacementExtent,PlacementCenter+PlacementExtent).ExpandBy(FVector(Radius,Radius,Half)).IsInside(Upright.UnrotateVector(P-Target)))continue;
    if(SafePassengers.ContainsByPredicate([&](const FVector& Other){return FVector::Dist2D(P,Other)<Radius*2+20;}))continue;
    SafePassengers.Add(P);Safe=true;break;
   }
   if(!Safe){Supported=false;break;}
  }
  if(!Supported)continue;Chosen=Target;Found=true;break;
 }
 if(!Found)return Fail(TEXT("No clear supported recovery position; move nearby obstructions"));
 // All placements were validated before mutating occupancy, resources or physics.
 for(int32 i=0;i<Evacuate.Num();++i)
 {
  auto* C=Evacuate[i];if(auto* PS=C->GetPlayerState<ARVPlayerState>())PS->Needs->EndRestAuthority(true);
  C->MulticastRecoveryPlacement(SafePassengers[i],FRotator(0,C->GetActorRotation().Yaw,0));
 }
 RV->MulticastClearRecoveryDrive();RV->Electrical->bEngineIdleRequested=false;
 auto* Movement=CastChecked<UChaosWheeledVehicleMovementComponent>(RV->GetVehicleMovement());Movement->ResetVehicleState();
 RV->SetActorLocationAndRotation(Chosen,Upright,false,nullptr,ETeleportType::TeleportPhysics);
 RV->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);RV->GetMesh()->SetPhysicsAngularVelocityInDegrees(FVector::ZeroVector);RV->GetMesh()->WakeAllRigidBodies();
 StableTime=0;bConfirmedOverturned=false;++RecoveryRevision;RecoveryGraceUntil=GetWorld()->GetTimeSeconds()+2;RV->SetAuthorityDriveLock(RV,true);RV->ForceNetUpdate();
 Feedback=TEXT("Prototype RV recovery complete; release driving controls before resuming");return true;
}
bool URVRecoveryComponent::DebugOverturn(float Roll)
{
#if !UE_BUILD_SHIPPING && !UE_BUILD_TEST
 auto* RV=Cast<ARVMechanicalMotorhome>(GetOwner());if(!RV || !RV->HasAuthority() || !GetWorld()->IsPlayInEditor() || !FMath::IsFinite(Roll))return false;
 RV->MulticastClearRecoveryDrive();RV->Electrical->bEngineIdleRequested=false;
 RV->SetActorRotation(FRotator(0,RV->GetActorRotation().Yaw,Roll),ETeleportType::TeleportPhysics);RV->GetMesh()->SetPhysicsLinearVelocity(FVector::ZeroVector);RV->GetMesh()->SetPhysicsAngularVelocityInDegrees(FVector::ZeroVector);RV->ForceNetUpdate();return true;
#else
 return false;
#endif
}
AActor* URVRecoveryComponent::DebugCreateSurface(FVector Location,FRotator Rotation,FVector Extent,bool bPawnSurface)
{
#if !UE_BUILD_SHIPPING && !UE_BUILD_TEST
 if(!GetWorld() || !GetWorld()->IsGameWorld() || Location.ContainsNaN() || Rotation.ContainsNaN() || Extent.ContainsNaN() || Extent.GetMin()<=0)return nullptr;
 // Local, disposable test fixture in each process, never an editor asset.
 AActor* Surface=nullptr;UStaticMeshComponent* Mesh=nullptr;
 if(bPawnSurface)
 {
  Surface=GetWorld()->SpawnActor<APawn>(Location,Rotation);
  if(!Surface)return nullptr;
  Mesh=NewObject<UStaticMeshComponent>(Surface);Surface->AddInstanceComponent(Mesh);Surface->SetRootComponent(Mesh);
  Mesh->SetMobility(EComponentMobility::Movable);
  Mesh->RegisterComponent();
 }
 else
 {
  auto* Static=GetWorld()->SpawnActor<AStaticMeshActor>(Location,Rotation);
  if(!Static)return nullptr;Surface=Static;Mesh=Static->GetStaticMeshComponent();
 }
 Mesh->SetMobility(EComponentMobility::Movable);
 Mesh->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));
 Mesh->SetCollisionProfileName(TEXT("BlockAll"));
 if(bPawnSurface)Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
 Surface->SetActorLocationAndRotation(Location,Rotation);Surface->SetActorScale3D(Extent/50);return Surface;
#else
 return nullptr;
#endif
}
