#include "Vehicles/RVVehicleSeatComponent.h"
#include "Player/RVSurvivorCharacter.h"
#include "Net/UnrealNetwork.h"
URVVehicleSeatComponent::URVVehicleSeatComponent() { SetIsReplicatedByDefault(true); }
void URVVehicleSeatComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(URVVehicleSeatComponent, Occupant); }
