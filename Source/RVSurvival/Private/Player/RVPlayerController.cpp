#include "Player/RVPlayerController.h"
#include "Player/RVInputMappings.h"
#include "UI/RVControlsWidget.h"
#include "InputActionValue.h"
#include "Mechanical/RVServicePoint.h"
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
DOREPLIFETIME_CONDITION(ARVPlayerController, ResourceFeedback, COND_OwnerOnly); DOREPLIFETIME_CONDITION(ARVPlayerController,MechanicalPoint,COND_OwnerOnly);DOREPLIFETIME_CONDITION(ARVPlayerController,MechanicalFeedback,COND_OwnerOnly); }
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
    if (!IsLocalController()) return;
    // PlayerController setup may precede local EnhancedInput user-settings init.
    // Retry idempotently after init so cab/rear/rest controls appear in the menu.
    if(ResourceMapping)RVInputMappings::Register(this,ResourceMapping);
    if(DrivingControlsCatalog)RVInputMappings::Register(this,DrivingControlsCatalog);
    // Service-only bindings must not consume remapped gameplay keys elsewhere.
    if (MechanicalMapping && bMechanicalMappingActive!=IsValid(MechanicalPoint))
        if (auto* Local=GetLocalPlayer()) if(auto* Input=Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
        {
            bMechanicalMappingActive=IsValid(MechanicalPoint);
            if(bMechanicalMappingActive) Input->AddMappingContext(MechanicalMapping,3);
            else Input->RemoveMappingContext(MechanicalMapping);
        }
}
void ARVPlayerController::DriverKey()
{ if(SeatedVehicle)for(auto* Seat:SeatedVehicle->GetSeats())if(Seat->bDriverSeat){RequestSwitchSeat(Seat->GetFName());break;} }
void ARVPlayerController::PassengerKey()
{ if(SeatedVehicle)for(auto* Seat:SeatedVehicle->GetSeats())if(!Seat->bDriverSeat && !Seat->bInteriorOnly){RequestSwitchSeat(Seat->GetFName());break;} }
void ARVPlayerController::NextSeatKey()
{
    if(!SeatedVehicle)return;
    const auto Seats=SeatedVehicle->GetSeats();int32 Current=INDEX_NONE;
    for(int32 Index=0;Index<Seats.Num();++Index)
        if(Seats[Index]->Occupant && Seats[Index]->OccupantController.Get()==this)Current=Index;
    for(int32 Offset=1;Offset<Seats.Num();++Offset)
    {auto* Seat=Seats[(Current+Offset+Seats.Num())%Seats.Num()];if(!Seat->Occupant){RequestSwitchSeat(Seat->GetFName());return;}}
    SeatFeedback=TEXT("No other seat is available.");
}
void ARVPlayerController::OrbitHold(const FInputActionValue& Value){bOrbitHeld=Value.Get<bool>();}
void ARVPlayerController::OrbitYaw(const FInputActionValue& Value)
{if(bOrbitHeld && GetPawn()==SeatedVehicle)if(auto* RV=Cast<ARVMotorhome>(SeatedVehicle))RV->OrbitCamera(Value.Get<float>(),0);}
void ARVPlayerController::OrbitPitch(const FInputActionValue& Value)
{if(bOrbitHeld && GetPawn()==SeatedVehicle)if(auto* RV=Cast<ARVMotorhome>(SeatedVehicle))RV->OrbitCamera(0,-Value.Get<float>());}
void ARVPlayerController::ToggleControls()
{
    if(!IsLocalController())return;
    if(ControlsWidget){ControlsWidget->RemoveFromParent();ControlsWidget=nullptr;SetInputMode(FInputModeGameOnly());bShowMouseCursor=false;ResetIgnoreMoveInput();ResetIgnoreLookInput();}
    else
    {FlushPressedKeys();ControlsWidget=CreateWidget<URVControlsWidget>(this);ControlsWidget->AddToViewport(20);ControlsWidget->SetDesiredSizeInViewport(FVector2D(640,650));ControlsWidget->SetPositionInViewport(FVector2D(40,40));FInputModeUIOnly Mode;Mode.SetWidgetToFocus(ControlsWidget->TakeWidget());SetInputMode(Mode);bShowMouseCursor=true;SetIgnoreMoveInput(true);SetIgnoreLookInput(true);}
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
    if(HasAuthority() && IsValid(MechanicalPoint) && MechanicalPoint->RepairPlayer && MechanicalPoint->RepairPlayer==PlayerState)
        MechanicalPoint->CancelAuthority(TEXT("Repair canceled: player disconnected; supplies retained"));
    if(HasAuthority()) if(auto* PS=GetPlayerState<ARVPlayerState>()) PS->Needs->EndRestAuthority(true);
    // The default implementation destroys the possessed pawn. A disconnected driver
    // must release possession before that path, or the shared RV would be destroyed.
    if (HasAuthority() && SeatedVehicle) SeatedVehicle->ReleaseDisconnected(this);
    Super::PawnLeavingGame();
}
void ARVPlayerController::EndPlay(const EEndPlayReason::Type Reason)
{
    if(ControlsWidget){ControlsWidget->RemoveFromParent();ControlsWidget=nullptr;}
    RVInputMappings::Unregister(ResourceInputLocalPlayer.Get(),ResourceMapping);
    RVInputMappings::Unregister(ResourceInputLocalPlayer.Get(),DrivingControlsCatalog);
    if(HasAuthority() && IsValid(MechanicalPoint) && MechanicalPoint->RepairPlayer && MechanicalPoint->RepairPlayer==PlayerState)
        MechanicalPoint->CancelAuthority(TEXT("Repair canceled: player left; supplies retained"));
    if(auto* Local=ResourceInputLocalPlayer.Get()) if(auto* Input=Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
    { if(ResourceMapping) Input->RemoveMappingContext(ResourceMapping); if(MechanicalMapping) Input->RemoveMappingContext(MechanicalMapping); }
    ResourceInputLocalPlayer.Reset(); bMechanicalMappingActive=false;
    if(HasAuthority()) if(auto* PS=GetPlayerState<ARVPlayerState>()) PS->Needs->EndRestAuthority();
    if(HasAuthority() && SeatedVehicle) SeatedVehicle->ReleaseDisconnected(this);
    Super::EndPlay(Reason);
}

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
        // Register driving defaults for the Controls menu before first possession.
        // This catalog is never applied to gameplay input and owns no vehicle/world references.
        DrivingControlsCatalog=NewObject<UInputMappingContext>(this);
        const FKey Keys[]={EKeys::W,EKeys::S,EKeys::D,EKeys::A,EKeys::SpaceBar,EKeys::E};
        const TCHAR* DrivingNames[]={TEXT("Accelerate"),TEXT("BrakeReverse"),TEXT("SteerRight"),TEXT("SteerLeft"),TEXT("Handbrake"),TEXT("VehicleExit")};
        const TCHAR* DrivingLabels[]={TEXT("Accelerate"),TEXT("Brake / reverse"),TEXT("Steer right"),TEXT("Steer left"),TEXT("Handbrake"),TEXT("Exit vehicle")};
        for(int32 i=0;i<UE_ARRAY_COUNT(Keys);++i)
            RVInputMappings::Map(DrivingControlsCatalog,NewObject<UInputAction>(DrivingControlsCatalog),Keys[i],DrivingNames[i],DrivingLabels[i]);
        ResourceMapping=NewObject<UInputMappingContext>(this);
        for(FKey Key:{EKeys::H,EKeys::J,EKeys::K,EKeys::L,EKeys::O,EKeys::Escape,EKeys::R,EKeys::Z,EKeys::Three,EKeys::One,EKeys::Two,EKeys::V,EKeys::F10,EKeys::RightMouseButton,EKeys::MouseX,EKeys::MouseY})
        {
            auto* Action=NewObject<UInputAction>(this); Action->ValueType=EInputActionValueType::Boolean;
            const int32 Index=ResourceActions.Num();
            const TCHAR* Names[]={TEXT("Lights"),TEXT("Generator"),TEXT("Fridge"),TEXT("StationPower"),TEXT("EngineIdle"),TEXT("ClosePanel"),TEXT("Stand"),TEXT("Sleep"),TEXT("RearInterior"),TEXT("DriverSeat"),TEXT("PassengerSeat"),TEXT("NextSeat"),TEXT("Controls"),TEXT("OrbitHold"),TEXT("OrbitYaw"),TEXT("OrbitPitch")};
            const TCHAR* Labels[]={TEXT("Lights"),TEXT("Generator"),TEXT("Fridge"),TEXT("Station power"),TEXT("Engine idle"),TEXT("Close panel"),TEXT("Stand from bed"),TEXT("Rest / sleep"),TEXT("Move to rear living area"),TEXT("Driver seat"),TEXT("Passenger seat"),TEXT("Next seat (stopped)"),TEXT("Controls menu"),TEXT("Orbit camera hold"),TEXT("Orbit horizontal"),TEXT("Orbit vertical")};
            if(Index>=14){Action->ValueType=EInputActionValueType::Axis1D;Action->bConsumeInput=false;}
            RVInputMappings::Map(ResourceMapping,Action,Key,FName(Names[Index]),Labels[Index]);ResourceActions.Add(Action);
        }
    }
    Input->BindAction(ResourceActions[0],ETriggerEvent::Started,this,&ThisClass::LightsKey);
    Input->BindAction(ResourceActions[1],ETriggerEvent::Started,this,&ThisClass::GeneratorKey);
    Input->BindAction(ResourceActions[2],ETriggerEvent::Started,this,&ThisClass::FridgeKey);
    Input->BindAction(ResourceActions[3],ETriggerEvent::Started,this,&ThisClass::StationKey);
    Input->BindAction(ResourceActions[4],ETriggerEvent::Started,this,&ThisClass::IdleKey);
    Input->BindAction(ResourceActions[5],ETriggerEvent::Started,this,&ThisClass::CloseKey);
    Input->BindAction(ResourceActions[6],ETriggerEvent::Started,this,&ThisClass::WakeKey);
    Input->BindAction(ResourceActions[7],ETriggerEvent::Started,this,&ThisClass::SleepKey);
    Input->BindAction(ResourceActions[8],ETriggerEvent::Started,this,&ThisClass::RequestLivingArea);
    Input->BindAction(ResourceActions[9],ETriggerEvent::Started,this,&ThisClass::DriverKey);
    Input->BindAction(ResourceActions[10],ETriggerEvent::Started,this,&ThisClass::PassengerKey);
    Input->BindAction(ResourceActions[11],ETriggerEvent::Started,this,&ThisClass::NextSeatKey);
    Input->BindAction(ResourceActions[12],ETriggerEvent::Started,this,&ThisClass::ToggleControls);
    for(auto Event:{ETriggerEvent::Triggered,ETriggerEvent::Completed,ETriggerEvent::Canceled})Input->BindAction(ResourceActions[13],Event,this,&ThisClass::OrbitHold);
    Input->BindAction(ResourceActions[14],ETriggerEvent::Triggered,this,&ThisClass::OrbitYaw);
    Input->BindAction(ResourceActions[15],ETriggerEvent::Triggered,this,&ThisClass::OrbitPitch);
    RVInputMappings::Register(this,ResourceMapping);
    if(!MechanicalMapping)
    {
        MechanicalMapping=NewObject<UInputMappingContext>(this);
        for(FKey Key:{EKeys::B,EKeys::N,EKeys::M,EKeys::P})
        {
            auto* Action=NewObject<UInputAction>(this); Action->ValueType=EInputActionValueType::Boolean;
            MechanicalMapping->MapKey(Action,Key); MechanicalActions.Add(Action);
        }
    }
    Input->BindAction(MechanicalActions[0],ETriggerEvent::Started,this,&ThisClass::PatchKey);
    Input->BindAction(MechanicalActions[1],ETriggerEvent::Started,this,&ThisClass::RadiatorKey);
    Input->BindAction(MechanicalActions[2],ETriggerEvent::Started,this,&ThisClass::EngineRepairKey);
    Input->BindAction(MechanicalActions[3],ETriggerEvent::Started,this,&ThisClass::HoodKey);
    if(auto* Subsystem=Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
    { ResourceInputLocalPlayer=Local; Subsystem->RemoveMappingContext(ResourceMapping); Subsystem->AddMappingContext(ResourceMapping,2); }
}
void ARVPlayerController::WakeKey()
{ if (auto* PS=GetPlayerState<ARVPlayerState>()) PS->Needs->RequestRestMode(ERVRestMode::Awake); }
void ARVPlayerController::SleepKey()
{ if (auto* PS=GetPlayerState<ARVPlayerState>()) PS->Needs->RequestRestMode(PS->Needs->State.RestMode==ERVRestMode::Sleeping?ERVRestMode::Resting:ERVRestMode::Sleeping); }
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
void ARVPlayerController::CloseKey() { if(ResourcePoint) RequestCloseResource(); if(MechanicalPoint)RequestService(TEXT("Close"),-1,FGuid(),-1); }
void ARVPlayerController::RequestService(FName Action,int32 Expected,FGuid Item,int32 ItemRevision)
{
    if(!IsLocalController())return;
    GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Action,Expected,Item,ItemRevision]
    {if(IsLocalController())ServerService(Action,Expected,Item,ItemRevision);}));
}
void ARVPlayerController::ServerService_Implementation(FName Action,int32 Expected,FGuid Item,int32 ItemRevision)
{
    if(!HasAuthority() || !IsValid(MechanicalPoint))return;
    MechanicalPoint->RequestAuthority(this,Action,Expected,Item,ItemRevision);
}
void ARVPlayerController::PatchKey(){if(MechanicalPoint)RequestService(TEXT("Patch"),MechanicalPoint->Revision,FGuid(),-1);}
void ARVPlayerController::RadiatorKey(){if(MechanicalPoint)RequestService(TEXT("ReplaceRadiator"),MechanicalPoint->Revision,FGuid(),-1);}
void ARVPlayerController::EngineRepairKey(){if(MechanicalPoint)RequestService(TEXT("EngineService"),MechanicalPoint->Revision,FGuid(),-1);}
void ARVPlayerController::HoodKey(){if(MechanicalPoint)RequestService(TEXT("Hood"),MechanicalPoint->Revision,FGuid(),-1);}
