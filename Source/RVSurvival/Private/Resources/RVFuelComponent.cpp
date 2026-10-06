#include "Resources/RVFuelComponent.h"
#include "Net/UnrealNetwork.h"
#include "NativeGameplayTags.h"
#include "HAL/IConsoleManager.h"
UE_DEFINE_GAMEPLAY_TAG_STATIC(FuelGasoline,"Resource.Fuel.Gasoline");
UE_DEFINE_GAMEPLAY_TAG_STATIC(FuelDiesel,"Resource.Fuel.Diesel");
UE_DEFINE_GAMEPLAY_TAG_STATIC(FuelPropane,"Resource.Fuel.Propane");
static TAutoConsoleVariable<int32> ResourceDebug(TEXT("rv.Resources.AllowDebug"),0,TEXT("Enable development-only authoritative resource controls"));
URVFuelComponent::URVFuelComponent() { SetIsReplicatedByDefault(true); FuelType=FuelGasoline; }
bool URVFuelComponent::DebugAllowed() {
#if !UE_BUILD_SHIPPING
    return ResourceDebug.GetValueOnGameThread()!=0;
#else
    return false;
#endif
}
void URVFuelComponent::BeginPlay()
{
    Super::BeginPlay();
    if(GetOwner()->HasAuthority())
    { CapacityLitres=FMath::IsFinite(CapacityLitres)?FMath::Max(0.,CapacityLitres):0;
      Litres=FMath::IsFinite(InitialLitres)?FMath::Clamp(InitialLitres,0.,CapacityLitres):0; OnRep_Fuel(); }
}
void URVFuelComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(URVFuelComponent,CapacityLitres); DOREPLIFETIME(URVFuelComponent,FuelType); DOREPLIFETIME(URVFuelComponent,Litres); }
void URVFuelComponent::OnRep_Fuel() { OnFuelChanged.Broadcast(); }
double URVFuelComponent::AddAuthority(double Amount)
{
    if(!GetOwner()->HasAuthority() || !FMath::IsFinite(Amount) || Amount<=0) return 0;
    const double Added=FMath::Min(Amount,FMath::Max(0.,CapacityLitres-Litres));
    Litres+=Added; if(Added>0) { OnRep_Fuel(); GetOwner()->ForceNetUpdate(); } return Added;
}
double URVFuelComponent::BurnAuthority(double Amount)
{
    if(!GetOwner()->HasAuthority() || !FMath::IsFinite(Amount) || Amount<=0) return 0;
    const double Burned=FMath::Min(Amount,Litres); Litres=FMath::Max(0.,Litres-Burned);
    if(Burned>0) { OnRep_Fuel(); GetOwner()->ForceNetUpdate(); } return Burned;
}
bool URVFuelComponent::DebugSetFuel(double Amount)
{
    if(!DebugAllowed() || !GetOwner()->HasAuthority() || !FMath::IsFinite(Amount)) return false;
    Litres=FMath::Clamp(Amount,0.,CapacityLitres); OnRep_Fuel(); GetOwner()->ForceNetUpdate(); return true;
}
