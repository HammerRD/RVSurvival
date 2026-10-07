#include "Mechanical/RVServicePoint.h"
#include "Mechanical/RVCoolingComponent.h"
#include "Vehicles/RVMechanicalMotorhome.h"
#include "Player/RVPlayerController.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
#include "Inventory/RVInventoryComponent.h"
#include "Interaction/RVInteractionTargetPresentationComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Net/UnrealNetwork.h"
#include "TimerManager.h"
#include "Vehicles/RVInteractiveDoor.h"
ARVServicePoint::ARVServicePoint()
{
    bAlwaysRelevant=true;SetReplicateMovement(true);PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.TickInterval=.1f;
    Mesh->SetRelativeScale3D(FVector(.06,.65,.4));Mesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);Mesh->SetCollisionResponseToAllChannels(ECR_Ignore);Mesh->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
    CreateDefaultSubobject<URVInteractionTargetPresentationComponent>(TEXT("TargetPresentation"));
}
void ARVServicePoint::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps)const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(ARVServicePoint,Vehicle);DOREPLIFETIME(ARVServicePoint,RepairPlayer);DOREPLIFETIME(ARVServicePoint,ActiveRepair);DOREPLIFETIME(ARVServicePoint,RepairStart);DOREPLIFETIME(ARVServicePoint,RepairDuration);DOREPLIFETIME(ARVServicePoint,Revision);}
FText ARVServicePoint::GetInteractionText_Implementation(APawn*)const{return FText::FromString(TEXT("Hold E: inspect engine / cooling service"));}
bool ARVServicePoint::HasAccess(const ARVPlayerController* PC)const
{
    const auto* P=PC?Cast<ARVSurvivorCharacter>(PC->GetPawn()):nullptr;
    if(!Vehicle || !P || PC->SeatedVehicle || !P->GetController())return false;
    const auto* PS=PC->GetPlayerState<ARVPlayerState>();if(!PS || PS->Needs->State.RestMode!=ERVRestMode::Awake)return false;
    FVector Eye;FRotator Rotation;P->GetActorEyesViewPoint(Eye,Rotation);
    if(FVector::DistSquared(Eye,GetActorLocation())>FMath::Square(300.f))return false;
    FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(RVServiceAccess),false,P);
    return !GetWorld()->LineTraceSingleByChannel(Hit,Eye,GetActorLocation(),ECC_Visibility,Params) || Hit.GetActor()==this;
}
void ARVServicePoint::CompleteInteraction_Implementation(APawn* P)
{
    auto* PC=P?Cast<ARVPlayerController>(P->GetController()):nullptr;
    if(!HasAuthority() || !HasAccess(PC))return;
    if(PC->MechanicalPoint && PC->MechanicalPoint!=this && PC->MechanicalPoint->RepairPlayer==PC->PlayerState)PC->MechanicalPoint->CancelAuthority(TEXT("Service changed"));
    PC->MechanicalPoint=this;PC->MechanicalFeedback=TEXT("Engine off and cool before servicing | B patch / N replace radiator / M engine service");PC->ForceNetUpdate();
}
void ARVServicePoint::RequestAuthority(ARVPlayerController* PC,FName Action,int32 Expected,FGuid Item,int32 ItemRevision)
{
    if(!HasAuthority() || !PC)return;
    auto Feedback=[&](FString Message){PC->MechanicalFeedback=MoveTemp(Message);PC->ForceNetUpdate();};
    if(Action==TEXT("Close")){if(RepairController.Get()==PC)CancelAuthority(TEXT("Repair canceled"));PC->MechanicalPoint=nullptr;Feedback(TEXT(""));return;}
    if(Action==TEXT("Cancel")){if(RepairController.Get()==PC)CancelAuthority(TEXT("Repair canceled; supplies retained"));return;}
    if(!HasAccess(PC) || PC->MechanicalPoint!=this){Feedback(TEXT("Service out of reach or incompatible state"));return;}
    if(Expected!=Revision){Feedback(TEXT("Service changed; refresh and retry"));return;}
    if(Action==TEXT("Hood"))
    {
        if(Vehicle->GetVelocity().Size()>=10 || !Vehicle->EngineHood){Feedback(TEXT("Stop before operating the hood"));return;}
        const bool WasOpen=Vehicle->EngineHood->bOpen;Vehicle->EngineHood->CompleteInteraction_Implementation(PC->GetPawn());
        if(WasOpen==Vehicle->EngineHood->bOpen){Feedback(TEXT("Hood swing obstructed; move clear"));return;}
        ++Revision;ForceNetUpdate();Feedback(Vehicle->EngineHood->bOpen?TEXT("Hood open; engine interlock active"):TEXT("Hood closed"));return;
    }
    auto* System=Vehicle->CoolingSystem.Get();
    if(Vehicle->EngineHood && !Vehicle->EngineHood->bOpen){Feedback(TEXT("Open the hood first (P)"));return;}
    if(!System->CanService()){Feedback(TEXT("Stop, switch off engine and let it cool before service"));return;}
    if(RepairPlayer){Feedback(TEXT("Another repair is already in progress"));return;}
    auto* Inv=PC->GetPawn()->FindComponentByClass<URVInventoryComponent>();if(!Inv)return;
    if(Action==TEXT("Refill"))
    {
        const double Free=FMath::Max(0.,System->Tuning.CoolantCapacityLitres-System->Cooling.CoolantLitres);double Drained=0;FString Error;
        if(Free<=1e-9){Feedback(TEXT("Cooling system full"));return;}
        if(!Inv->DrainFluidAuthority(Item,ItemRevision,URVItemDefinition::FindRegisteredTag(TEXT("Resource.Fluid.Coolant")),Free,Drained,Error)){Feedback(Error);return;}
        const double Added=System->AddCoolantAuthority(Drained);check(FMath::IsNearlyEqual(Drained,Added,1e-8));++Revision;ForceNetUpdate();Feedback(FString::Printf(TEXT("Added %.3f L coolant"),Added));return;
    }
    const auto* R=System->Profile?System->Profile->Repairs.FindByPredicate([&](const auto& X){return X.Id==Action;}):nullptr;
    if(!R || !FMath::IsFinite(R->DurationSeconds) || R->DurationSeconds<=0 || R->DurationSeconds>300 || !FMath::IsFinite(R->RadiatorConditionTarget) || !FMath::IsFinite(R->EngineConditionTarget) || !FMath::IsFinite(R->LeakMultiplier))
    {Feedback(TEXT("Unknown or invalid repair"));return;}
    if((!R->bAffectsCooling || (System->Cooling.RadiatorCondition>=R->RadiatorConditionTarget && System->Cooling.PatchLeakMultiplier<=R->LeakMultiplier)) && (!R->bAffectsEngine || System->Engine.Condition>=FMath::Min(R->EngineConditionTarget,System->Tuning.EngineMaximumCondition)))
    {Feedback(TEXT("This repair would not improve the current fault"));return;}
    FString Error;if(!Inv->RepairRequirementsAuthority(R->Requirements,false,Error)){Feedback(Error);return;}
    RepairController=PC;RepairPlayer=PC->PlayerState;ActiveRepair=Action;RepairStart=GetWorld()->GetTimeSeconds();RepairDuration=R->DurationSeconds;ExpectedMechanicalRevision=System->ServiceRevision;++Revision;
    GetWorldTimerManager().SetTimer(Completion,this,&ThisClass::FinishRepair,RepairDuration,false);ForceNetUpdate();Feedback(TEXT("Repairing | stay at engine bay | Escape cancels"));
}
void ARVServicePoint::Tick(float DT)
{
    Super::Tick(DT);if(!HasAuthority())return;
    for(auto It=GetWorld()->GetPlayerControllerIterator();It;++It)
        if(auto* Viewer=Cast<ARVPlayerController>(It->Get());Viewer && Viewer->MechanicalPoint==this && !HasAccess(Viewer))
        {Viewer->MechanicalPoint=nullptr;Viewer->MechanicalFeedback=TEXT("Service closed: out of reach or incompatible state");Viewer->ForceNetUpdate();}
    if(!RepairPlayer)return;
    auto* PC=RepairController.Get();auto* Inv=PC && PC->GetPawn()?PC->GetPawn()->FindComponentByClass<URVInventoryComponent>():nullptr;
    if(!PC || !HasAccess(PC) || PC->MechanicalPoint!=this || PC->ResourcePoint || !Inv || Inv->OpenContainer || (Vehicle->EngineHood && !Vehicle->EngineHood->bOpen) || !Vehicle->CoolingSystem->CanService() || Vehicle->CoolingSystem->ServiceRevision!=ExpectedMechanicalRevision)
        CancelAuthority(TEXT("Repair interrupted; supplies retained"));
}
void ARVServicePoint::FinishRepair()
{
    auto* PC=RepairController.Get();auto* System=Vehicle?Vehicle->CoolingSystem.Get():nullptr;
    if(!HasAuthority() || !PC || !System || !HasAccess(PC) || PC->MechanicalPoint!=this || (Vehicle->EngineHood && !Vehicle->EngineHood->bOpen) || !System->CanService() || ExpectedMechanicalRevision!=System->ServiceRevision)
    {CancelAuthority(TEXT("Repair interrupted; supplies retained"));return;}
    const auto* R=System->Profile?System->Profile->Repairs.FindByPredicate([&](const auto& X){return X.Id==ActiveRepair;}):nullptr;
    auto* Inv=PC->GetPawn()->FindComponentByClass<URVInventoryComponent>();FString Error;
    if(!R || !Inv || PC->ResourcePoint || Inv->OpenContainer || !Inv->RepairRequirementsAuthority(R->Requirements,true,Error)){CancelAuthority(Error.IsEmpty()?TEXT("Repair no longer available or incompatible action"):Error);return;}
    System->ApplyRepairAuthority(*R);CancelAuthority(TEXT("Repair complete; refill coolant before continuing"));
}
void ARVServicePoint::CancelAuthority(const FString& Reason)
{
    if(!HasAuthority())return;
    GetWorldTimerManager().ClearTimer(Completion);
    if(auto* PC=RepairController.Get()){PC->MechanicalFeedback=Reason;PC->ForceNetUpdate();}
    RepairController.Reset();RepairPlayer=nullptr;ActiveRepair=NAME_None;RepairStart=0;RepairDuration=0;ExpectedMechanicalRevision=-1;++Revision;ForceNetUpdate();
}
void ARVServicePoint::EndPlay(EEndPlayReason::Type Reason){if(HasAuthority())CancelAuthority(TEXT("Service ended"));Super::EndPlay(Reason);}
