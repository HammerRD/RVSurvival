#include "Resources/RVElectricalComponent.h"
#include "Core/RVGameState.h"

#include "Vehicles/RVSystemsMotorhome.h"
#include "Net/UnrealNetwork.h"
URVElectricalComponent::URVElectricalComponent()
{
    SetIsReplicatedByDefault(true);
    FRVElectricalLoad Lights; Lights.Id=TEXT("InteriorLights"); Lights.DisplayName=FText::FromString(TEXT("Interior lights")); Lights.Watts=24; Lights.Priority=1;
    FRVElectricalLoad Fridge; Fridge.Id=TEXT("Refrigerator"); Fridge.DisplayName=FText::FromString(TEXT("Refrigerator")); Fridge.Watts=90; Fridge.Priority=2; Fridge.bEnabled=true;
    FRVElectricalLoad Station; Station.Id=TEXT("PoweredStation"); Station.DisplayName=FText::FromString(TEXT("Powered equipment")); Station.Watts=120; Station.Priority=3;
    Tuning.Loads={Lights,Fridge,Station};
}
void URVElectricalComponent::BeginPlay()
{
    Super::BeginPlay();
    if(!GetOwner()->HasAuthority()) return;
    if(Profile) Tuning=Profile->Values;
    // Bad content cannot create negative burn or infinite/free source output.
    double* Rates[]={&Tuning.IdleLitresPerHour,&Tuning.ThrottleLitresPerHour,&Tuning.RoadLitresPerHour,
      &Tuning.GeneratorLitresPerHour,&Tuning.GeneratorWatts,&Tuning.GeneratorReserveLitres,
      &Tuning.AlternatorHouseWatts,&Tuning.AlternatorChassisWatts,&Tuning.SolarPeakWatts,
      &Tuning.ShoreWatts,&Tuning.GeneratorNoiseStrength};
    for(auto* Rate:Rates) *Rate=FMath::IsFinite(*Rate)?FMath::Max(0.,*Rate):0;
    TArray<ERVPowerSource> Priority;
    for(auto S:Tuning.SourcePriority) if(S!=ERVPowerSource::Battery && uint8(S)<uint8(ERVPowerSource::Battery)) Priority.AddUnique(S);
    for(auto S:{ERVPowerSource::Shore,ERVPowerSource::Generator,ERVPowerSource::Alternator,ERVPowerSource::Solar}) Priority.AddUnique(S);
    Priority.Add(ERVPowerSource::Battery); Tuning.SourcePriority=Priority;
    TSet<FName> Names; Loads.Reset();
    for(auto L:Tuning.Loads) if(!L.Id.IsNone() && !Names.Contains(L.Id) && FMath::IsFinite(L.Watts) && L.Watts>0)
    { Names.Add(L.Id); L.bPowered=false; Loads.Add(L); }
    Loads.StableSort([](const auto& A,const auto& B){return A.Priority<B.Priority;});
    OnRep_Power();
}
void URVElectricalComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(URVElectricalComponent,Tuning); DOREPLIFETIME(URVElectricalComponent,Loads);
    DOREPLIFETIME(URVElectricalComponent,bGeneratorRunning); DOREPLIFETIME(URVElectricalComponent,bEngineIdleRequested);
    DOREPLIFETIME(URVElectricalComponent,SolarInput); DOREPLIFETIME(URVElectricalComponent,bShoreConnected);
    DOREPLIFETIME(URVElectricalComponent,bEngineRunning); DOREPLIFETIME(URVElectricalComponent,Flow);
    DOREPLIFETIME(URVElectricalComponent,ControlRevision);
}
void URVElectricalComponent::OnRep_Power()
{
    OnPowerChanged.Broadcast();
    if(bReportedGeneratorNoise!=bGeneratorRunning)
    { bReportedGeneratorNoise=bGeneratorRunning; OnGeneratorNoiseChanged.Broadcast(); }
}
bool URVElectricalComponent::IsLoadPowered(FName Id) const
{ const auto* L=Loads.FindByPredicate([&](const auto& X){return X.Id==Id;}); return L && L->bPowered; }
bool URVElectricalComponent::HasHousePower() const
{ const auto* V=Cast<ARVSystemsMotorhome>(GetOwner()); return V && ((V->HouseBattery->EnergyWh>0 && V->HouseBattery->MaxDischargeWatts>0) || Flow.AvailableSourceWatts>0); }
bool URVElectricalComponent::SetControlAuthority(FName Control,bool Enabled,int32 Expected,FString& Error)
{
    if(!GetOwner()->HasAuthority()) { Error=TEXT("Authority required"); return false; }
    if(Expected!=ControlRevision) { Error=TEXT("Panel changed; refresh and retry"); return false; }
    auto* V=Cast<ARVSystemsMotorhome>(GetOwner()); if(!V) return false;
    if(Control==TEXT("Generator"))
    {
        auto* Fuel=Tuning.bSharedGeneratorFuel?V->PropulsionFuel.Get():V->GeneratorFuel.Get();
        if(Enabled && (Tuning.GeneratorLitresPerHour<=0 || Tuning.GeneratorWatts<=0 ||
            Fuel->Litres<=(Tuning.bSharedGeneratorFuel?Tuning.GeneratorReserveLitres:0)))
        { Error=TEXT("Generator fuel below usable reserve"); return false; }
        bGeneratorRunning=Enabled;
    }
    else if(Control==TEXT("EngineIdle")) bEngineIdleRequested=Enabled;
    else if(auto* Load=Loads.FindByPredicate([&](const auto& L){return L.Id==Control;})) Load->bEnabled=Enabled;
    else { Error=TEXT("Unknown panel control"); return false; }
    ++ControlRevision; Error.Empty(); OnRep_Power(); GetOwner()->ForceNetUpdate(); return true;
}
void URVElectricalComponent::AdvanceAuthority(double Seconds,bool EngineOperating,double Throttle,double Speed)
{
    auto* V=Cast<ARVSystemsMotorhome>(GetOwner());
    if(!V || !V->HasAuthority() || !FMath::IsFinite(Seconds) || Seconds<=0 || !FMath::IsFinite(Throttle) || !FMath::IsFinite(Speed)) return;
    const double Hours=Seconds/3600.;
    bEngineRunning=EngineOperating && V->PropulsionFuel->Litres>0;
    double EngineFraction=0;
    if(bEngineRunning)
    {
        const double Wanted=(Tuning.IdleLitresPerHour+Tuning.ThrottleLitresPerHour*FMath::Clamp(FMath::Abs(Throttle),0.,1.)+
            Tuning.RoadLitresPerHour*FMath::Clamp(FMath::Abs(Speed)/2682.24,0.,2.))*Hours*ARVGameState::Multiplier(this,TEXT("Fuel"));
        EngineFraction=Wanted>0?V->PropulsionFuel->BurnAuthority(Wanted)/Wanted:1;
        bEngineRunning=V->PropulsionFuel->Litres>0;
    }
    double GeneratorFraction=0;
    if(bGeneratorRunning)
    {
        auto* Fuel=Tuning.bSharedGeneratorFuel?V->PropulsionFuel.Get():V->GeneratorFuel.Get();
        const double Usable=FMath::Max(0.,Fuel->Litres-(Tuning.bSharedGeneratorFuel?Tuning.GeneratorReserveLitres:0));
        const double Wanted=Tuning.GeneratorLitresPerHour*Hours*ARVGameState::Multiplier(this,TEXT("GeneratorFuel"));
        if(Wanted>0) GeneratorFraction=Fuel->BurnAuthority(FMath::Min(Wanted,Usable))/Wanted;
        if(GeneratorFraction<1-1e-9 || Usable<=0) { bGeneratorRunning=false; ++ControlRevision; }
    }
    Flow=FRVPowerFlow();
    double SourceWh[4]={bShoreConnected?Tuning.ShoreWatts*Hours:0,Tuning.GeneratorWatts*GeneratorFraction*Hours,
        Tuning.AlternatorHouseWatts*EngineFraction*Hours,Tuning.SolarPeakWatts*FMath::Clamp(SolarInput,0.,1.)*Hours};
    for(int i=0;i<4;++i) Flow.AvailableSourceWatts+=SourceWh[i]/Hours;
    double BatteryAllowance=FMath::Min(V->HouseBattery->EnergyWh,FMath::Max(0.,V->HouseBattery->MaxDischargeWatts)*Hours);
    double ChassisAllowance=FMath::Min(V->ChassisBattery->EnergyWh,FMath::Max(0.,V->ChassisBattery->MaxDischargeWatts)*Hours);
    double HouseUsed=0,ChassisUsed=0;
    double ChassisSource=Tuning.AlternatorChassisWatts*EngineFraction*Hours;
    for(auto& L:Loads)
    {
        L.bPowered=false; if(!L.bEnabled) continue;
        Flow.RequestedWatts+=L.Watts;
        const double Need=L.Watts*Hours;
        if(L.Domain==ERVPowerDomain::Chassis)
        {
            const double Delivered=FMath::Min(Need,ChassisAllowance+ChassisSource);
            if(Delivered>0)
            { const double Generated=FMath::Min(Delivered,ChassisSource); ChassisSource-=Generated;
              ChassisAllowance-=Delivered-Generated; ChassisUsed+=Delivered-Generated;
              if(Generated>0) Flow.ActiveSources.AddUnique(ERVPowerSource::Alternator);
              L.bPowered=Delivered>=Need*(1-1e-9); Flow.SuppliedWatts+=Delivered/Hours; }
            continue;
        }
        double Available=BatteryAllowance; for(double X:SourceWh) Available+=X;
        // Account the final fractional interval when a battery exhausts.
        // Full-power status still requires the complete requested interval; no dimming model.
        const double Delivered=FMath::Min(Need,Available);
        if(Delivered<=0) continue;
        double Remaining=Delivered;
        for(auto S:Tuning.SourcePriority)
        {
            if(Remaining<=0) break;
            double Used=0;
            if(S==ERVPowerSource::Battery) { Used=FMath::Min(Remaining,BatteryAllowance); BatteryAllowance-=Used; HouseUsed+=Used; }
            else { Used=FMath::Min(Remaining,SourceWh[int(S)]); SourceWh[int(S)]-=Used; }
            if(Used>0) Flow.ActiveSources.AddUnique(S);
            Remaining-=Used;
        }
        L.bPowered=Delivered>=Need*(1-1e-9); Flow.SuppliedWatts+=Delivered/Hours;
    }
    V->HouseBattery->DischargeAuthority(HouseUsed,Hours); V->ChassisBattery->DischargeAuthority(ChassisUsed,Hours);
    // Charge once with remaining generated input; sources spent on loads cannot be spent twice.
    double Spare=0; for(double X:SourceWh) Spare+=X;
    const double Charged=HouseUsed>0?0:V->HouseBattery->ChargeAuthority(Spare,Hours);
    double UnassignedCharge=Charged;
    for(auto S:Tuning.SourcePriority) if(S!=ERVPowerSource::Battery && UnassignedCharge>0)
    { double Used=FMath::Min(SourceWh[int(S)],UnassignedCharge); UnassignedCharge-=Used; if(Used>0) Flow.ActiveSources.AddUnique(S); }
    Flow.HouseBatteryWatts=(Charged-HouseUsed)/Hours;
    Flow.ChassisChargeWatts=V->ChassisBattery->ChargeAuthority(ChassisSource,Hours)/Hours;
    OnRep_Power(); V->ForceNetUpdate();
}
bool URVElectricalComponent::DebugAdvance(double Seconds,bool Engine,double Throttle,double Speed)
{
    if(!URVFuelComponent::DebugAllowed() || !GetOwner()->HasAuthority() || !FMath::IsFinite(Seconds) || Seconds<=0 || Seconds>86400) return false;
    // Bounded substeps exercise transitions/reserves rather than bypassing them in one huge integration.
    while(Seconds>0) { double Step=FMath::Min(Seconds,1.); AdvanceAuthority(Step,Engine,Throttle,Speed); Seconds-=Step; }
    return true;
}
bool URVElectricalComponent::DebugSetSolar(double Scalar)
{
    if(!URVFuelComponent::DebugAllowed() || !GetOwner()->HasAuthority() || !FMath::IsFinite(Scalar)) return false;
    SolarInput=FMath::Clamp(Scalar,0.,1.); GetOwner()->ForceNetUpdate(); return true;
}
bool URVElectricalComponent::DebugSetTimeScale(double Scalar)
{
    if(!URVFuelComponent::DebugAllowed() || !GetOwner()->HasAuthority() || !FMath::IsFinite(Scalar)) return false;
    TimeScale=FMath::Clamp(Scalar,.01,1000.); return true;
}

FString URVElectricalComponent::GetSourceSummary() const
{
    FString Text;
    for(auto Source:Flow.ActiveSources)
    { if(!Text.IsEmpty()) Text+=TEXT(" + "); Text+=StaticEnum<ERVPowerSource>()->GetNameStringByValue(int64(Source)); }
    return Text.IsEmpty()?(HasHousePower()?TEXT("Battery ready / no active draw"):TEXT("No usable power")):Text;
}
bool URVElectricalComponent::SetExternalPowerAuthority(bool Connected)
{
    if(!GetOwner()->HasAuthority()) return false;
    bShoreConnected=Connected; GetOwner()->ForceNetUpdate(); return true;
}
