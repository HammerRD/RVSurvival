#include "Player/RVPlayerController.h"
#include "Vehicles/RVVehicleBase.h"
#include "Net/UnrealNetwork.h"
#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
void ARVPlayerController::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME_CONDITION(ARVPlayerController, SeatedVehicle, COND_OwnerOnly); }
void ARVPlayerController::ServerDrive_Implementation(float Throttle, float Steering, bool Handbrake)
{ if (SeatedVehicle) SeatedVehicle->ReceiveDriveInput(this, Throttle, Steering, Handbrake); }
void ARVPlayerController::ServerExitVehicle_Implementation()
{ if (SeatedVehicle && GetWorld()->GetTimeSeconds() - SeatEntryTime > .75) SeatedVehicle->TryExit(this); }
void ARVPlayerController::PawnLeavingGame()
{
    if(HasAuthority()) if(auto* PS=GetPlayerState<ARVPlayerState>()) PS->Needs->EndRestAuthority();
    // The default implementation destroys the possessed pawn. A disconnected driver
    // must release possession before that path, or the shared RV would be destroyed.
    if (HasAuthority() && SeatedVehicle) SeatedVehicle->ReleaseDisconnected(this);
    Super::PawnLeavingGame();
}
void ARVPlayerController::EndPlay(const EEndPlayReason::Type Reason)
{ if(HasAuthority()) if(auto* PS=GetPlayerState<ARVPlayerState>()) PS->Needs->EndRestAuthority(); if (HasAuthority() && SeatedVehicle) SeatedVehicle->ReleaseDisconnected(this); Super::EndPlay(Reason); }
