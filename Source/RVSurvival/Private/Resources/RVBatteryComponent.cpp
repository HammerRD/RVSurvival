#include "Resources/RVBatteryComponent.h"
#include "Net/UnrealNetwork.h"
URVBatteryComponent::URVBatteryComponent() { SetIsReplicatedByDefault(true); }
void URVBatteryComponent::BeginPlay()
{
    Super::BeginPlay();
    if(GetOwner()->HasAuthority())
    { CapacityWh=FMath::IsFinite(CapacityWh)?FMath::Max(0.,CapacityWh):0;
      EnergyWh=FMath::IsFinite(InitialWh)?FMath::Clamp(InitialWh,0.,CapacityWh):0; OnRep_Energy(); }
}
void URVBatteryComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(URVBatteryComponent,Domain); DOREPLIFETIME(URVBatteryComponent,CapacityWh); DOREPLIFETIME(URVBatteryComponent,EnergyWh); DOREPLIFETIME(URVBatteryComponent,MaxChargeWatts); DOREPLIFETIME(URVBatteryComponent,MaxDischargeWatts); }
void URVBatteryComponent::OnRep_Energy() { OnEnergyChanged.Broadcast(); }
double URVBatteryComponent::ChargeAuthority(double Wh,double Hours)
{
    if(!GetOwner()->HasAuthority() || !FMath::IsFinite(Wh) || !FMath::IsFinite(Hours) || Wh<=0 || Hours<=0) return 0;
    const double Added=FMath::Max(0.,FMath::Min3(Wh,CapacityWh-EnergyWh,FMath::Max(0.,MaxChargeWatts)*Hours));
    EnergyWh+=Added; if(Added>0) { OnRep_Energy(); GetOwner()->ForceNetUpdate(); } return Added;
}
double URVBatteryComponent::DischargeAuthority(double Wh,double Hours)
{
    if(!GetOwner()->HasAuthority() || !FMath::IsFinite(Wh) || !FMath::IsFinite(Hours) || Wh<=0 || Hours<=0) return 0;
    const double Used=FMath::Max(0.,FMath::Min3(Wh,EnergyWh,FMath::Max(0.,MaxDischargeWatts)*Hours));
    EnergyWh-=Used; if(Used>0) { OnRep_Energy(); GetOwner()->ForceNetUpdate(); } return Used;
}
bool URVBatteryComponent::DebugSetEnergy(double Wh)
{
    if(!URVFuelComponent::DebugAllowed() || !GetOwner()->HasAuthority() || !FMath::IsFinite(Wh)) return false;
    EnergyWh=FMath::Clamp(Wh,0.,CapacityWh); OnRep_Energy(); GetOwner()->ForceNetUpdate(); return true;
}
