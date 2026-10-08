#include "Medical/RVMedicalStation.h"
#include "Player/RVPlayerController.h"
#include "Player/RVSurvivorCharacter.h"
#include "Inventory/RVInventoryComponent.h"
#include "Net/UnrealNetwork.h"
ARVMedicalStation::ARVMedicalStation() { StationName=TEXT("Medical station"); }
void ARVMedicalStation::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(ARVMedicalStation,LinkedStorage); }
FText ARVMedicalStation::GetInteractionText_Implementation(APawn*) const
{ return NSLOCTEXT("RV","MedicalStationPrompt","Hold E: medical station / supplies"); }
bool ARVMedicalStation::IsReachable(const ARVSurvivorCharacter* Character) const
{
    if(!Character || FVector::Dist(Character->GetActorLocation(),GetActorLocation())>300) return false;
    FCollisionQueryParams Params; Params.AddIgnoredActor(Character); Params.AddIgnoredActor(this);
    return !GetWorld()->LineTraceTestByChannel(Character->GetActorLocation(),GetActorLocation(),ECC_Visibility,Params);
}
void ARVMedicalStation::CompleteInteraction_Implementation(APawn* Pawn)
{
    auto* Character=Cast<ARVSurvivorCharacter>(Pawn);
    if(!HasAuthority() || !CanInteract_Implementation(Pawn) || !IsReachable(Character)) return;
    Super::CompleteInteraction_Implementation(Pawn);
    if(auto* PC=Cast<ARVPlayerController>(Pawn->GetController()))
    {
        PC->MedicalStation=this; PC->ClientOpenMedical(); PC->ForceNetUpdate();
        if(LinkedStorage) if(auto* Inventory=Pawn->FindComponentByClass<URVInventoryComponent>()) Inventory->OpenContainerAuthority(LinkedStorage);
    }
}
