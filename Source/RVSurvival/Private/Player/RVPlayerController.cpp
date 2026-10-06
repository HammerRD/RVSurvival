#include "Player/RVPlayerController.h"
#include "Vehicles/RVResourcePoint.h"
#include "Vehicles/RVSystemsMotorhome.h"
#include "Resources/RVElectricalComponent.h"
#include "Inventory/RVInventoryComponent.h"
#include "Vehicles/RVVehicleBase.h"
#include "Net/UnrealNetwork.h"
#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
#include "Vehicles/RVVehicleSeatComponent.h"
#include "Vehicles/RVInteriorMotorhome.h"
#include "TimerManager.h"
#include "InputCoreTypes.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"
#include "InputAction.h"
#include "Engine/LocalPlayer.h"
#include "Player/RVSurvivorCharacter.h"
void ARVPlayerController::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME_CONDITION(ARVPlayerController, SeatedVehicle, COND_OwnerOnly); DOREPLIFETIME_CONDITION(ARVPlayerController, SeatFeedback, COND_OwnerOnly);
DOREPLIFETIME_CONDITION(ARVPlayerController, ResourcePoint, COND_OwnerOnly);
DOREPLIFETIME_CONDITION(ARVPlayerController, ResourceFeedback, COND_OwnerOnly); }
void ARVPlayerController::RequestSwitchSeat(FName TargetSeat)
{
    if (!IsLocalController() || !SeatedVehicle) return;
    GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this, [this, TargetSeat]()
    { if (IsLocalController() && SeatedVehicle) ServerSwitchSeat(TargetSeat); }));
}
void ARVPlayerController::ServerSwitchSeat_Implementation(FName TargetSeat)
{
    if (!HasAuthority() || !SeatedVehicle) return;
    const double Now = GetWorld()->GetTimeSeconds();
    if (Now - LastSeatSwitchTime < .25) return;
    LastSeatSwitchTime = Now; SeatedVehicle->TrySwitchSeat(this, TargetSeat); ForceNetUpdate();
}
void ARVPlayerController::PlayerTick(float DeltaTime)
{
    Super::PlayerTick(DeltaTime);
    if (IsLocalController())
    {
        if (auto* PS=GetPlayerState<ARVPlayerState>())
        {
            if (WasInputKeyJustPressed(EKeys::R)) PS->Needs->RequestRestMode(ERVRestMode::Awake);
            if (WasInputKeyJustPressed(EKeys::Z)) PS->Needs->RequestRestMode(PS->Needs->State.RestMode==ERVRestMode::Sleeping?ERVRestMode::Resting:ERVRestMode::Sleeping);
        }
        if (WasInputKeyJustPressed(EKeys::Three)) RequestLivingArea();
    }
    if (!IsLocalController() || !SeatedVehicle) return;
    const auto Seats = SeatedVehicle->GetSeats();
    if (WasInputKeyJustPressed(EKeys::One))
        for (auto* Seat : Seats) if (Seat->bDriverSeat) { RequestSwitchSeat(Seat->GetFName()); break; }
    if (WasInputKeyJustPressed(EKeys::Two))
        for (auto* Seat : Seats) if (!Seat->bDriverSeat) { RequestSwitchSeat(Seat->GetFName()); break; }
    if (WasInputKeyJustPressed(EKeys::V))
    {
        int32 Current = INDEX_NONE;
        for (int32 Index=0; Index<Seats.Num(); ++Index)
            if (Seats[Index]->Occupant && ((Seats[Index]->bDriverSeat && GetPawn()==SeatedVehicle)
                || GetPawn()==Seats[Index]->Occupant)) Current=Index;
        for (int32 Offset=1; Offset<Seats.Num(); ++Offset)
        { auto* Seat=Seats[(Current+Offset+Seats.Num())%Seats.Num()]; if (!Seat->Occupant) { RequestSwitchSeat(Seat->GetFName()); return; } }
        SeatFeedback=TEXT("No other seat is available.");
    }
}
void ARVPlayerController::RequestLivingArea()
{
    if (!IsLocalController() || !SeatedVehicle) return;
    GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this]{ServerLivingArea();}));
}
void ARVPlayerController::ServerLivingArea_Implementation()
{
    if (!HasAuthority() || GetWorld()->GetTimeSeconds()-LastSeatSwitchTime<.25) return;
    LastSeatSwitchTime=GetWorld()->GetTimeSeconds();
    if (auto* RV=Cast<ARVInteriorMotorhome>(SeatedVehicle)) RV->TryMoveToLivingArea(this);
    ForceNetUpdate();
}
void ARVPlayerController::ServerDrive_Implementation(float Throttle, float Steering, bool Handbrake)
{ if (SeatedVehicle) SeatedVehicle->ReceiveDriveInput(this, Throttle, Steering, Handbrake); }
void ARVPlayerController::ServerExitVehicle_Implementation()
{ if (SeatedVehicle && GetWorld()->GetTimeSeconds() - SeatEntryTime > .75) SeatedVehicle->TryExit(this); }
void ARVPlayerController::PawnLeavingGame()
{
    if(HasAuthority()) if(auto* PS=GetPlayerState<ARVPlayerState>()) PS->Needs->EndRestAuthority(true);
    // The default implementation destroys the possessed pawn. A disconnected driver
    // must release possession before that path, or the shared RV would be destroyed.
    if (HasAuthority() && SeatedVehicle) SeatedVehicle->ReleaseDisconnected(this);
    Super::PawnLeavingGame();
}
void ARVPlayerController::EndPlay(const EEndPlayReason::Type Reason)
{ if(auto* Local=ResourceInputLocalPlayer.Get()) if(auto* Input=Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>()) if(ResourceMapping) Input->RemoveMappingContext(ResourceMapping); ResourceInputLocalPlayer.Reset(); if(HasAuthority()) if(auto* PS=GetPlayerState<ARVPlayerState>()) PS->Needs->EndRestAuthority(); if (HasAuthority() && SeatedVehicle) SeatedVehicle->ReleaseDisconnected(this); Super::EndPlay(Reason); }

bool ARVPlayerController::ValidateResourceAccess(bool Fill) const
{
    const APawn* P=GetPawn();
    if(!HasAuthority() || !P || !IsValid(ResourcePoint) || !IsValid(ResourcePoint->Vehicle) || ResourcePoint->bFuelFill!=Fill) return false;
    if(Fill && ResourcePoint->Vehicle->GetVelocity().Size()>150) return false;
    FVector Eye; FRotator R; P->GetActorEyesViewPoint(Eye,R);
    const FVector Target=ResourcePoint->GetActorLocation();
    if(FVector::DistSquared(Eye,Target)>FMath::Square(300.f)) return false;
    FHitResult Hit; FCollisionQueryParams Params(SCENE_QUERY_STAT(RVResourceAccess),false,P);
    return !GetWorld()->LineTraceSingleByChannel(Hit,Eye,Target,ECC_Visibility,Params) || Hit.GetActor()==ResourcePoint;
}
void ARVPlayerController::RequestResourceControl(FName Control,bool Enabled,int32 Revision)
{
    if(!IsLocalController()) return;
    GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Control,Enabled,Revision]()
    { if(IsLocalController()) ServerResourceControl(Control,Enabled,Revision); }));
}
void ARVPlayerController::RequestRefuel(FGuid Id,int32 Revision)
{
    if(!IsLocalController()) return;
    GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Id,Revision]()
    { if(IsLocalController()) ServerRefuel(Id,Revision); }));
}
void ARVPlayerController::RequestCloseResource()
{
    if(IsLocalController()) RequestResourceControl(TEXT("Close"),false,-1);
}
void ARVPlayerController::ServerResourceControl_Implementation(FName Control,bool Enabled,int32 Revision)
{
    if(!HasAuthority()) return;
    if(Control==TEXT("Close")) { ResourcePoint=nullptr; ResourceFeedback.Empty(); ForceNetUpdate(); return; }
    if(!ValidateResourceAccess(false)) { ResourceFeedback=TEXT("Panel out of reach or blocked"); ResourcePoint=nullptr; ForceNetUpdate(); return; }
    const double Now=GetWorld()->GetTimeSeconds();
    if(Now-LastResourceRequestTime<.1) { ResourceFeedback=TEXT("Please wait"); return; }
    LastResourceRequestTime=Now;
    ResourcePoint->Vehicle->Electrical->SetControlAuthority(Control,Enabled,Revision,ResourceFeedback); ForceNetUpdate();
}
void ARVPlayerController::ServerRefuel_Implementation(FGuid Id,int32 Revision)
{
    if(!HasAuthority()) return;
    if(!ValidateResourceAccess(true)) { ResourceFeedback=TEXT("Fuel fill out of reach, blocked or RV moving"); ForceNetUpdate(); return; }
    auto* Inv=GetPawn()->FindComponentByClass<URVInventoryComponent>();
    double Amount=0;
    if(Inv && Inv->RefuelAuthority(ResourcePoint->Vehicle->PropulsionFuel,Id,Revision,Amount,ResourceFeedback))
        ResourceFeedback=FString::Printf(TEXT("Transferred %.3f L"),Amount);
    ForceNetUpdate();
}

void ARVPlayerController::SetupInputComponent()
{
    Super::SetupInputComponent();
    auto* Local=GetLocalPlayer(); auto* Input=Cast<UEnhancedInputComponent>(InputComponent);
    if(!Local || !Input) return;
    if(!ResourceMapping)
    {
        ResourceMapping=NewObject<UInputMappingContext>(this);
        for(FKey Key:{EKeys::H,EKeys::J,EKeys::K,EKeys::L,EKeys::O,EKeys::Escape})
        {
            auto* Action=NewObject<UInputAction>(this); Action->ValueType=EInputActionValueType::Boolean;
            ResourceMapping->MapKey(Action,Key); ResourceActions.Add(Action);
        }
    }
    Input->BindAction(ResourceActions[0],ETriggerEvent::Started,this,&ThisClass::LightsKey);
    Input->BindAction(ResourceActions[1],ETriggerEvent::Started,this,&ThisClass::GeneratorKey);
    Input->BindAction(ResourceActions[2],ETriggerEvent::Started,this,&ThisClass::FridgeKey);
    Input->BindAction(ResourceActions[3],ETriggerEvent::Started,this,&ThisClass::StationKey);
    Input->BindAction(ResourceActions[4],ETriggerEvent::Started,this,&ThisClass::IdleKey);
    Input->BindAction(ResourceActions[5],ETriggerEvent::Started,this,&ThisClass::CloseKey);
    if(auto* Subsystem=Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
    { ResourceInputLocalPlayer=Local; Subsystem->RemoveMappingContext(ResourceMapping); Subsystem->AddMappingContext(ResourceMapping,2); }
}
void ARVPlayerController::ToggleResource(FName Control)
{
    if(!IsLocalController() || !IsValid(ResourcePoint) || ResourcePoint->bFuelFill || !ResourcePoint->Vehicle) return;
    auto* Bus=ResourcePoint->Vehicle->Electrical.Get();
    bool Enabled=false;
    if(Control==TEXT("Generator")) Enabled=Bus->bGeneratorRunning;
    else if(Control==TEXT("EngineIdle")) Enabled=Bus->bEngineIdleRequested;
    else if(const auto* Load=Bus->Loads.FindByPredicate([&](const auto& L){return L.Id==Control;})) Enabled=Load->bEnabled;
    else return;
    RequestResourceControl(Control,!Enabled,Bus->ControlRevision);
}
void ARVPlayerController::LightsKey() { ToggleResource(TEXT("InteriorLights")); }
void ARVPlayerController::GeneratorKey() { ToggleResource(TEXT("Generator")); }
void ARVPlayerController::FridgeKey() { ToggleResource(TEXT("Refrigerator")); }
void ARVPlayerController::StationKey() { ToggleResource(TEXT("PoweredStation")); }
void ARVPlayerController::IdleKey() { ToggleResource(TEXT("EngineIdle")); }
void ARVPlayerController::CloseKey() { if(ResourcePoint) RequestCloseResource(); }
