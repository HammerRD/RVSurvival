#include "Mechanical/RVCoolingComponent.h"
#include "Vehicles/RVSystemsMotorhome.h"
#include "Resources/RVElectricalComponent.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "Net/UnrealNetwork.h"
#include "NativeGameplayTags.h"
UE_DEFINE_GAMEPLAY_TAG_STATIC(CoolingLeak,"Vehicle.Fault.Cooling.Leak");
UE_DEFINE_GAMEPLAY_TAG_STATIC(RadiatorDamage,"Vehicle.Fault.Cooling.RadiatorDamage");
UE_DEFINE_GAMEPLAY_TAG_STATIC(CoolingLow,"Vehicle.Fault.Cooling.LowCoolant");
UE_DEFINE_GAMEPLAY_TAG_STATIC(CoolingOverheat,"Vehicle.Fault.Cooling.Overheat");
UE_DEFINE_GAMEPLAY_TAG_STATIC(EngineDamaged,"Vehicle.Fault.Engine.Damaged");
URVCoolingComponent::URVCoolingComponent()
{SetIsReplicatedByDefault(true);PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.TickInterval=.25f;}
void URVCoolingComponent::BeginPlay()
{
    Super::BeginPlay(); AddTickPrerequisiteActor(GetOwner());
    if(!GetOwner()->HasAuthority())return;
    if(Profile)Tuning=Profile->Tuning;
    double* NonNegative[]={&Tuning.IdleHeatCPerSecond,&Tuning.LoadHeatCPerSecond,&Tuning.PassiveCoolingPerSecond,&Tuning.RadiatorCoolingPerSecond,&Tuning.AirflowBonus,&Tuning.MinorLeakLitresPerSecond,&Tuning.MajorLeakLitresPerSecond};
    for(auto* V:NonNegative)*V=FMath::IsFinite(*V)?FMath::Clamp(*V,0.,100.):0;
    Tuning.CoolantCapacityLitres=FMath::IsFinite(Tuning.CoolantCapacityLitres)?FMath::Clamp(Tuning.CoolantCapacityLitres,.1,1000.):12;
    Tuning.LowCoolantFraction=FMath::IsFinite(Tuning.LowCoolantFraction)?FMath::Clamp(Tuning.LowCoolantFraction,0.,1.):.25;
    Tuning.AmbientC=FMath::IsFinite(Tuning.AmbientC)?FMath::Clamp(Tuning.AmbientC,-50.,60.):20;
    Tuning.WarmC=FMath::IsFinite(Tuning.WarmC)?FMath::Clamp(Tuning.WarmC,70.,150.):95;
    Tuning.HotC=FMath::IsFinite(Tuning.HotC)?FMath::Clamp(Tuning.HotC,Tuning.WarmC+1,170.):105;
    Tuning.OverheatC=FMath::IsFinite(Tuning.OverheatC)?FMath::Clamp(Tuning.OverheatC,Tuning.HotC+1,180.):115;
    Tuning.CriticalC=FMath::IsFinite(Tuning.CriticalC)?FMath::Clamp(Tuning.CriticalC,Tuning.OverheatC+1,190.):130;
    Tuning.MaximumTemperatureC=FMath::IsFinite(Tuning.MaximumTemperatureC)?FMath::Clamp(Tuning.MaximumTemperatureC,Tuning.CriticalC+1,250.):200;
    Tuning.SafeServiceC=FMath::IsFinite(Tuning.SafeServiceC)?FMath::Clamp(Tuning.SafeServiceC,Tuning.AmbientC,Tuning.HotC):60;
    Tuning.RestartTemperatureC=FMath::IsFinite(Tuning.RestartTemperatureC)?FMath::Clamp(Tuning.RestartTemperatureC,Tuning.SafeServiceC,Tuning.OverheatC):105;
    Tuning.MinorDamageThreshold=FMath::IsFinite(Tuning.MinorDamageThreshold)?FMath::Clamp(Tuning.MinorDamageThreshold,.1f,1.f):.85f;
    Tuning.MajorDamageThreshold=FMath::IsFinite(Tuning.MajorDamageThreshold)?FMath::Clamp(Tuning.MajorDamageThreshold,0.f,Tuning.MinorDamageThreshold):.35f;
    Tuning.EngineDamagePerSecond=FMath::IsFinite(Tuning.EngineDamagePerSecond)?FMath::Clamp(Tuning.EngineDamagePerSecond,0.f,1.f):.0004f;
    Tuning.ShutdownCondition=FMath::IsFinite(Tuning.ShutdownCondition)?FMath::Clamp(Tuning.ShutdownCondition,0.f,.5f):.1f;
    Tuning.RestartCondition=FMath::IsFinite(Tuning.RestartCondition)?FMath::Clamp(Tuning.RestartCondition,Tuning.ShutdownCondition+.01f,1.f):.3f;
    Tuning.LimpOutput=FMath::IsFinite(Tuning.LimpOutput)?FMath::Clamp(Tuning.LimpOutput,0.f,1.f):.35f;
    Cooling.CoolantLitres=Tuning.CoolantCapacityLitres;Cooling.TemperatureC=Tuning.AmbientC;DeriveState();
}
void URVCoolingComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps)const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(URVCoolingComponent,Tuning);DOREPLIFETIME(URVCoolingComponent,Cooling);DOREPLIFETIME(URVCoolingComponent,Engine);DOREPLIFETIME(URVCoolingComponent,ServiceRevision);}
void URVCoolingComponent::OnRep_State(){OnStateChanged.Broadcast();}
void URVCoolingComponent::TickComponent(float DT,ELevelTick Type,FActorComponentTickFunction* Function)
{
    Super::TickComponent(DT,Type,Function);
    auto* RV=Cast<ARVSystemsMotorhome>(GetOwner());if(!RV || !RV->HasAuthority())return;
    auto* Move=Cast<UChaosWheeledVehicleMovementComponent>(RV->GetVehicleMovement());
    AdvanceAuthority(FMath::Min(double(DT),2.)*TimeScale,RV->Electrical->bEngineRunning,Move?Move->GetThrottleInput():0,RV->GetVelocity().Size());
}
void URVCoolingComponent::DeriveState()
{
    const auto& T=Tuning;
    Cooling.LeakLitresPerSecond=(Cooling.RadiatorCondition<=T.MajorDamageThreshold?T.MajorLeakLitresPerSecond:Cooling.RadiatorCondition<T.MinorDamageThreshold?T.MinorLeakLitresPerSecond:0)*Cooling.PatchLeakMultiplier;
    Cooling.CoolingEffectiveness=Cooling.RadiatorCondition*FMath::Clamp(Cooling.CoolantLitres/T.CoolantCapacityLitres,0.,1.);
    Cooling.Status=Cooling.TemperatureC>=T.CriticalC?ERVThermalStatus::Critical:Cooling.TemperatureC>=T.OverheatC?ERVThermalStatus::Overheating:Cooling.TemperatureC>=T.HotC?ERVThermalStatus::Hot:Cooling.TemperatureC>=T.WarmC?ERVThermalStatus::Warm:ERVThermalStatus::Normal;
    Cooling.Faults.Reset();if(Cooling.LeakLitresPerSecond>0)Cooling.Faults.AddTag(CoolingLeak);
    if(Cooling.RadiatorCondition<T.MinorDamageThreshold)Cooling.Faults.AddTag(RadiatorDamage);
    if(Cooling.CoolantLitres<T.CoolantCapacityLitres*T.LowCoolantFraction)Cooling.Faults.AddTag(CoolingLow);
    if(Cooling.Status>=ERVThermalStatus::Overheating)Cooling.Faults.AddTag(CoolingOverheat);
    if(Engine.Condition<.75f)Cooling.Faults.AddTag(EngineDamaged);
    if(Engine.Condition<=T.ShutdownCondition)Engine.bShutdown=true;
    if(Engine.bShutdown && Engine.Condition>=T.RestartCondition && Cooling.TemperatureC<T.RestartTemperatureC)Engine.bShutdown=false;
    Engine.OutputScale=Engine.bShutdown?0:Cooling.Status>=ERVThermalStatus::Overheating?T.LimpOutput:Engine.Condition<.5f?FMath::Max(T.LimpOutput,Engine.Condition):1;
}
void URVCoolingComponent::AdvanceAuthority(double Seconds,bool Running,double Load,double Speed)
{
    if(!GetOwner()->HasAuthority() || !FMath::IsFinite(Seconds) || Seconds<=0 || Seconds>86400 || !FMath::IsFinite(Load) || !FMath::IsFinite(Speed))return;
    for(double Left=Seconds;Left>1e-9;)
    {
        const double Step=FMath::Min(Left,1.);Left-=Step;DeriveState();
        Cooling.CoolantLitres=FMath::Max(0.,Cooling.CoolantLitres-Cooling.LeakLitresPerSecond*Step);
        const double Flow=1+Tuning.AirflowBonus*FMath::Clamp(FMath::Abs(Speed)/2682.24,0.,2.);
        const double Loss=Tuning.PassiveCoolingPerSecond+Tuning.RadiatorCoolingPerSecond*Cooling.CoolingEffectiveness*Flow;
        const double Heat=Running && !Engine.bShutdown?Tuning.IdleHeatCPerSecond+Tuning.LoadHeatCPerSecond*FMath::Clamp(FMath::Abs(Load),0.,1.):0;
        // Exact exponential solution of dT/dt=heat-k(T-ambient) is bounded even with accelerated steps.
        const double Decay=FMath::Exp(-Loss*Step);
        const double Next=Loss>1e-9?Tuning.AmbientC+(Cooling.TemperatureC-Tuning.AmbientC)*Decay+Heat/Loss*(1-Decay):Cooling.TemperatureC+Heat*Step;
        Cooling.TemperatureC=FMath::Clamp(Next,Tuning.AmbientC,Tuning.MaximumTemperatureC);
        if(Running && !Engine.bShutdown && Cooling.TemperatureC>=Tuning.OverheatC)
            Engine.Condition=FMath::Max(0.f,Engine.Condition-float(Step)*Tuning.EngineDamagePerSecond*float(FMath::Clamp((Cooling.TemperatureC-Tuning.OverheatC)/15.+1.,1.,6.)));
    }
    DeriveState();OnRep_State();GetOwner()->ForceNetUpdate();
}
bool URVCoolingComponent::CanService()const
{
    const auto* RV=Cast<ARVSystemsMotorhome>(GetOwner());
    return RV && RV->GetVelocity().Size()<10 && !RV->Electrical->bEngineRunning && Cooling.TemperatureC<=Tuning.SafeServiceC;
}
double URVCoolingComponent::AddCoolantAuthority(double Litres)
{
    if(!GetOwner()->HasAuthority() || !CanService() || !FMath::IsFinite(Litres) || Litres<=0)return 0;
    const double Amount=FMath::Min(Litres,FMath::Max(0.,Tuning.CoolantCapacityLitres-Cooling.CoolantLitres));
    if(Amount<=0)return 0;Cooling.CoolantLitres+=Amount;++ServiceRevision;DeriveState();OnRep_State();GetOwner()->ForceNetUpdate();return Amount;
}
void URVCoolingComponent::ApplyRepairAuthority(const FRVRepairDefinition& R)
{
    if(!GetOwner()->HasAuthority() || !CanService())return;
    if(R.bAffectsCooling)
    {
        Cooling.RadiatorCondition=FMath::Max(Cooling.RadiatorCondition,FMath::Clamp(R.RadiatorConditionTarget,0.f,1.f));
        Cooling.PatchLeakMultiplier=FMath::Clamp(R.LeakMultiplier,0.,1.);Cooling.bTemporaryPatch=R.bTemporary;
    }
    if(R.bAffectsEngine)Engine.Condition=FMath::Max(Engine.Condition,FMath::Clamp(R.EngineConditionTarget,0.f,1.f));
    ++ServiceRevision;DeriveState();OnRep_State();GetOwner()->ForceNetUpdate();
}
bool URVCoolingComponent::DebugSetState(float R,double C,double T,float E)
{
#if !UE_BUILD_SHIPPING && !UE_BUILD_TEST
    if(!GetOwner()->HasAuthority() || !GetWorld()->IsPlayInEditor() || !FMath::IsFinite(R) || !FMath::IsFinite(C) || !FMath::IsFinite(T) || !FMath::IsFinite(E))return false;
    Cooling.RadiatorCondition=FMath::Clamp(R,0.f,1.f);Cooling.CoolantLitres=FMath::Clamp(C,0.,Tuning.CoolantCapacityLitres);Cooling.TemperatureC=FMath::Clamp(T,Tuning.AmbientC,Tuning.MaximumTemperatureC);
    Engine.Condition=FMath::Clamp(E,0.f,1.f);Cooling.PatchLeakMultiplier=1;Cooling.bTemporaryPatch=false;Engine.bShutdown=false;++ServiceRevision;DeriveState();OnRep_State();GetOwner()->ForceNetUpdate();return true;
#else
    return false;
#endif
}
bool URVCoolingComponent::DebugAdvance(double Seconds,bool Running,double Load,double Speed)
{
#if !UE_BUILD_SHIPPING && !UE_BUILD_TEST
    if(!GetOwner()->HasAuthority() || !GetWorld()->IsPlayInEditor() || !FMath::IsFinite(Seconds) || Seconds<=0 || Seconds>86400)return false;
    AdvanceAuthority(Seconds,Running,Load,Speed);return true;
#else
    return false;
#endif
}
bool URVCoolingComponent::DebugSetTimeScale(double Scale)
{
#if !UE_BUILD_SHIPPING && !UE_BUILD_TEST
    if(!GetOwner()->HasAuthority() || !GetWorld()->IsPlayInEditor() || !FMath::IsFinite(Scale) || Scale<0 || Scale>1000)return false;TimeScale=Scale;return true;
#else
    return false;
#endif
}
