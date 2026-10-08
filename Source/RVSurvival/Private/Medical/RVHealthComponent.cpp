#include "Medical/RVHealthComponent.h"
#include "Vehicles/RVVehicleBase.h"
#include "Medical/RVMedicalAttributes.h"
#include "Medical/RVAnalgesicEffect.h"
#include "Medical/RVMedicalStation.h"
#include "Player/RVPlayerController.h"
#include "Player/RVPlayerState.h"
#include "Player/RVSurvivorCharacter.h"
#include "Survival/RVNeedsComponent.h"
#include "Inventory/RVInventoryComponent.h"
#include "AbilitySystemComponent.h"
#include "TimerManager.h"
#include "Net/UnrealNetwork.h"
#include "GameFramework/GameStateBase.h"
#include "NativeGameplayTags.h"
#include "HAL/IConsoleManager.h"
#include "Core/RVLog.h"
static TAutoConsoleVariable<int32> MedicalDebug(TEXT("rv.Medical.Debug"),0,TEXT("Development medical visibility diagnostics"));
#include "Player/RVPassengerReferenceFrameComponent.h"
static AActor* MedicalFrame(const ARVSurvivorCharacter* Character)
{const auto* Frame=Character?Character->FindComponentByClass<URVPassengerReferenceFrameComponent>():nullptr;return Frame?Frame->ReferenceFrame.Get():nullptr;}
static FVector MedicalPosition(const ARVSurvivorCharacter* Character)
{const auto* Frame=MedicalFrame(Character);return Frame?Frame->GetActorTransform().InverseTransformPosition(Character->GetActorLocation()):Character->GetActorLocation();}
UE_DEFINE_GAMEPLAY_TAG_STATIC(TAG_RVWound,"Medical.Injury.Wound");
UE_DEFINE_GAMEPLAY_TAG_STATIC(TAG_RVFracture,"Medical.Injury.Fracture");
UE_DEFINE_GAMEPLAY_TAG_STATIC(TAG_RVBurn,"Medical.Injury.Burn");
UE_DEFINE_GAMEPLAY_TAG_STATIC(TAG_RVConcussion,"Medical.Injury.Concussion");
UE_DEFINE_GAMEPLAY_TAG_STATIC(TAG_RVDowned,"Medical.Status.Downed");
UE_DEFINE_GAMEPLAY_TAG_STATIC(TAG_RVTerminal,"Medical.Status.Terminal");

URVHealthComponent::URVHealthComponent()
{
    SetIsReplicatedByDefault(true); PrimaryComponentTick.bCanEverTick=true;
    PrimaryComponentTick.TickInterval=.2f;
}
void URVHealthComponent::BeginPlay() { Super::BeginPlay(); }
void URVHealthComponent::EndPlay(const EEndPlayReason::Type Reason)
{
    if(GetOwner()->HasAuthority())
    {
        CancelTreatment(TEXT("Treatment ended"));
        if(ReservedBy.IsValid()) ReservedBy->CancelTreatment(TEXT("Patient disconnected"));
    }
    Super::EndPlay(Reason);
}
const URVMedicalProfile* URVHealthComponent::Tuning() const { return Profile?Profile.Get():GetDefault<URVMedicalProfile>(); }
void URVHealthComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(URVHealthComponent,Injuries); DOREPLIFETIME(URVHealthComponent,LifeState);
    DOREPLIFETIME_CONDITION(URVHealthComponent,Feedback,COND_OwnerOnly);
    DOREPLIFETIME(URVHealthComponent,ActiveTreatment); DOREPLIFETIME(URVHealthComponent,TreatmentEndTime);
}
float URVHealthComponent::GetMovementScale() const
{
    if(!CanAct()) return 0;
    float Scale=1;
    for(const auto& I:Injuries)
        if(I.Kind==ERVInjuryKind::Fracture && (I.Region==ERVBodyRegion::LeftLeg || I.Region==ERVBodyRegion::RightLeg) && I.Healing<1)
            Scale=FMath::Min(Scale,I.bStabilized?Tuning()->SplintedLegSpeedScale:Tuning()->UntreatedLegSpeedScale);
    return FMath::Clamp(Scale,0.f,1.f);
}
float URVHealthComponent::GetPain() const
{
    float Pain=0; for(const auto& I:Injuries) Pain+=I.Pain*(1-I.Healing);
    const auto* PS=Cast<ARVPlayerState>(GetOwner());
    return FMath::Clamp(Pain-(PS && PS->MedicalAttributes?PS->MedicalAttributes->GetAnalgesia():0),0.f,100.f);
}
FGameplayTagContainer URVHealthComponent::GetStatusTags() const
{
    FGameplayTagContainer Tags;
    for(const auto& I:Injuries) if(I.Healing<1 && I.InjuryTag.IsValid()) Tags.AddTag(I.InjuryTag);
    if(LifeState==ERVMedicalLifeState::Downed) Tags.AddTag(TAG_RVDowned);
    if(LifeState==ERVMedicalLifeState::Terminal) Tags.AddTag(TAG_RVTerminal);
    return Tags;
}
bool URVHealthComponent::DebugSetInfectionRisk(FGuid Injury,float Risk)
{
    if(!DebugAllowed() || !FMath::IsFinite(Risk)) return false;
    if(auto* I=Injuries.FindByPredicate([&](const auto& Entry){return Entry.Id==Injury;}))
    { I->InfectionRisk=FMath::Clamp(Risk,0.f,1.f);++I->Revision;GetOwner()->ForceNetUpdate();return true; }
    return false;
}
void URVHealthComponent::TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Function)
{
    Super::TickComponent(Delta,Type,Function);
    if(!GetOwner()->HasAuthority()) return;
    auto* PS=Cast<ARVPlayerState>(GetOwner()); if(!PS || !PS->MedicalAbilitySystem || !PS->MedicalAttributes) return;
    const float Seconds=FMath::Max(0.f,Delta)*TimeScale;
    float Bleed=0;
    for(auto& I:Injuries)
    {
        I.AgeSeconds+=Seconds; Bleed+=I.BleedingPerMinute;
        const bool Recoverable=I.Kind==ERVInjuryKind::Concussion || I.bTreated;
        const bool Nourished=PS->Needs->State.Nutrition>20 && PS->Needs->State.Hydration>20;
        if(Recoverable && I.BleedingPerMinute<=0 && I.InfectionRisk<.5f && Nourished)
            I.Healing=FMath::Clamp(I.Healing+Seconds/3600*Tuning()->HealingPerHour,0.f,1.f);
    }
    float Blood=PS->MedicalAttributes->GetBlood()-Bleed*Seconds/60;
    if(Bleed<=0 && LifeState==ERVMedicalLifeState::Active) Blood+=Tuning()->BloodRecoveryPerMinute*Seconds/60;
    PS->MedicalAbilitySystem->SetNumericAttributeBase(URVMedicalAttributes::GetBloodAttribute(),FMath::Clamp(Blood,0.f,100.f));
    // Stabilized, revived patients must be able to recover, rather than inevitably
    // deteriorating again before their deliberately slow blood recovery completes.
    float Vitality=PS->MedicalAttributes->GetVitality();
    if(Blood<Tuning()->CriticalBlood && (Bleed>0 || LifeState==ERVMedicalLifeState::Downed))
        Vitality-=FMath::Max(0.f,Tuning()->CriticalVitalityLossPerMinute)*Seconds/60;
    else if(Blood>=Tuning()->CriticalBlood && Bleed<=0 && LifeState==ERVMedicalLifeState::Active
            && PS->Needs->State.Nutrition>20 && PS->Needs->State.Hydration>20)
        Vitality+=FMath::Max(0.f,Tuning()->VitalityRecoveryPerMinute)*Seconds/60;
    PS->MedicalAbilitySystem->SetNumericAttributeBase(URVMedicalAttributes::GetVitalityAttribute(),FMath::Clamp(Vitality,0.f,100.f));
    UpdateLifeState(Seconds);
    if(ActiveTreatment.IsValid()) { FString Error; if(!ValidateTreatment(Error)) CancelTreatment(Error); }
}
void URVHealthComponent::UpdateLifeState(float Delta)
{
    const auto* PS=Cast<ARVPlayerState>(GetOwner());
    if(LifeState==ERVMedicalLifeState::Terminal) return;
    if(PS->MedicalAttributes->GetBlood()<=Tuning()->DownedBlood || PS->MedicalAttributes->GetVitality()<=5)
    {
        if(LifeState==ERVMedicalLifeState::Active) { LifeState=ERVMedicalLifeState::Downed; PS->Needs->EndRestAuthority(true); CancelTreatment(TEXT("Unable to continue")); }
        DownedSeconds+=Delta;
        if(DownedSeconds>=Tuning()->DownedTimeoutSeconds || PS->MedicalAttributes->GetBlood()<=0) LifeState=ERVMedicalLifeState::Terminal;
    }
}
bool URVHealthComponent::DebugAllowed() const
{
#if UE_BUILD_SHIPPING || UE_BUILD_TEST
    return false;
#else
    return GetOwner()->HasAuthority() && GetWorld() && GetWorld()->WorldType==EWorldType::PIE;
#endif
}
bool URVHealthComponent::DebugApplyInjury(ERVInjuryKind Kind,ERVBodyRegion Region,float Severity)
{
    if(!DebugAllowed() || !FMath::IsFinite(Severity) || uint8(Kind)>uint8(ERVInjuryKind::Concussion) || uint8(Region)>uint8(ERVBodyRegion::RightLeg)) return false;
    FRVInjuryInstance I; I.Id=FGuid::NewGuid(); I.Kind=Kind; I.Region=Region; I.Severity=FMath::Clamp(Severity,1.f,3.f);
    I.InjuryTag=Kind==ERVInjuryKind::Wound?TAG_RVWound:Kind==ERVInjuryKind::Fracture?TAG_RVFracture:Kind==ERVInjuryKind::Burn?TAG_RVBurn:TAG_RVConcussion;
    I.Pain=I.Severity*10; I.InfectionRisk=(Kind==ERVInjuryKind::Wound || Kind==ERVInjuryKind::Burn)?.4f:0;
    if(Kind==ERVInjuryKind::Wound) I.BleedingPerMinute=I.Severity<1.5f?Tuning()->MinorBleedPerMinute:(I.Severity<2.5f?Tuning()->ModerateBleedPerMinute:Tuning()->SevereBleedPerMinute);
    Injuries.Add(I); GetOwner()->ForceNetUpdate(); return true;
}
bool URVHealthComponent::ApplyWoundAuthority(ERVBodyRegion Region,float Severity,float Damage,float Contamination)
{
    if(!GetOwner() || !GetOwner()->HasAuthority() || LifeState==ERVMedicalLifeState::Terminal
        || uint8(Region)>uint8(ERVBodyRegion::RightLeg) || !FMath::IsFinite(Severity)
        || !FMath::IsFinite(Damage) || Damage<0 || !FMath::IsFinite(Contamination))return false;
    auto* PS=Cast<ARVPlayerState>(GetOwner());if(!PS)return false;
    auto& I=Injuries.AddDefaulted_GetRef();I.Id=FGuid::NewGuid();I.Kind=ERVInjuryKind::Wound;
    I.InjuryTag=TAG_RVWound;I.Region=Region;I.Severity=FMath::Clamp(Severity,1.f,3.f);
    I.Pain=I.Severity*10;I.InfectionRisk=FMath::Clamp(Contamination,0.f,1.f);
    const auto* P=Tuning();I.BleedingPerMinute=I.Severity<1.5f?P->MinorBleedPerMinute:I.Severity<2.5f?P->ModerateBleedPerMinute:P->SevereBleedPerMinute;
    PS->MedicalAbilitySystem->SetNumericAttributeBase(URVMedicalAttributes::GetVitalityAttribute(),
        FMath::Clamp(PS->MedicalAttributes->GetVitality()-Damage,0.f,100.f));
    UpdateLifeState(0);GetOwner()->ForceNetUpdate();return true;
}
bool URVHealthComponent::DebugSetVitals(float Blood,float Vitality)
{
    if(!DebugAllowed() || !FMath::IsFinite(Blood) || !FMath::IsFinite(Vitality)) return false;
    auto* PS=Cast<ARVPlayerState>(GetOwner());
    PS->MedicalAbilitySystem->SetNumericAttributeBase(URVMedicalAttributes::GetBloodAttribute(),FMath::Clamp(Blood,0.f,100.f));
    PS->MedicalAbilitySystem->SetNumericAttributeBase(URVMedicalAttributes::GetVitalityAttribute(),FMath::Clamp(Vitality,0.f,100.f));
    UpdateLifeState(0); return true;
}
bool URVHealthComponent::DebugSetTimeScale(float Scale) { if(!DebugAllowed() || !FMath::IsFinite(Scale)) return false; TimeScale=FMath::Clamp(Scale,.01f,10000.f); return true; }
bool URVHealthComponent::DebugClearInjuries()
{
    if(!DebugAllowed()) return false;
    CancelTreatment(TEXT("Debug reset")); Injuries.Empty(); LifeState=ERVMedicalLifeState::Active; DownedSeconds=0;
    return DebugSetVitals(100,100);
}
void URVHealthComponent::RequestTreatment(ARVPlayerState* Patient,FGuid Injury,FGuid Supply,int32 ExpectedRevision)
{
    TWeakObjectPtr<ARVPlayerState> WeakPatient(Patient);
    GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,WeakPatient,Injury,Supply,ExpectedRevision]{ServerBeginTreatment(WeakPatient.Get(),Injury,Supply,ExpectedRevision);}));
}
void URVHealthComponent::RequestCancelTreatment()
{ GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this]{ServerCancelTreatment();})); }
void URVHealthComponent::ServerBeginTreatment_Implementation(ARVPlayerState* Patient,FGuid Injury,FGuid Supply,int32 ExpectedRevision)
{
    if(!GetOwner()->HasAuthority() || !Injury.IsValid() || !Supply.IsValid() || ActiveTreatment.IsValid() || !Patient || !Patient->Health || Patient->Health->ReservedBy.IsValid()) return;
    TreatmentPatient=Patient; ActiveTreatment=Injury; SupplyId=Supply; InjuryRevision=ExpectedRevision;
    FString Error;
    if(!ValidateTreatment(Error)) { CancelTreatment(Error); return; }
    const auto* PS=Cast<ARVPlayerState>(GetOwner()); auto* Character=PS->Needs->ResolveSurvivor();
    const auto Items=Character->FindComponentByClass<URVInventoryComponent>()->GetItems();
    const auto* Item=Items.FindByPredicate([&](const auto& I){return I.Id==SupplyId;});
    Patient->Health->ReservedBy=this;
    HealerFrame=MedicalFrame(Character); HealerStart=MedicalPosition(Character);
    auto* PatientCharacter=Patient->Needs->ResolveSurvivor();
    PatientFrame=MedicalFrame(PatientCharacter); PatientStart=MedicalPosition(PatientCharacter);
    const float Duration=FMath::Max(.1f,Item->Definition->Medical.DurationSeconds);
    TreatmentEndTime=GetWorld()->GetGameState()->GetServerWorldTimeSeconds()+Duration;
    GetWorld()->GetTimerManager().SetTimer(TreatmentTimer,this,&URVHealthComponent::CompleteTreatment,Duration,false);
    Feedback=TEXT("Treatment started — cancel to stop"); GetOwner()->ForceNetUpdate();
}
bool URVHealthComponent::ValidateTreatment(FString& Error) const
{
    const auto* PS=Cast<ARVPlayerState>(GetOwner()); auto* Patient=TreatmentPatient.Get();
    auto* Healer=PS && PS->Needs?PS->Needs->ResolveSurvivor():nullptr;
    auto* Character=Patient && Patient->Needs?Patient->Needs->ResolveSurvivor():nullptr;
    auto* Health=Patient?Patient->Health.Get():nullptr;
    if(!CanAct() || !Healer || !Character || !Health || Health->LifeState==ERVMedicalLifeState::Terminal || Healer->SeatedVehicle)
    { Error=TEXT("Patient or treatment unavailable"); return false; }
    if(Character->SeatedVehicle && (Health->LifeState!=ERVMedicalLifeState::Downed || Character->SeatedVehicle->GetVelocity().Size()>30))
    { Error=TEXT("Stop the vehicle before treating a seated downed patient");return false; }
    if(Health->ReservedBy.IsValid() && Health->ReservedBy.Get()!=this) { Error=TEXT("Patient already being treated"); return false; }
    if(TreatmentEndTime>0 && (MedicalFrame(Healer)!=HealerFrame.Get() || MedicalFrame(Character)!=PatientFrame.Get() || FVector::Dist(MedicalPosition(Healer),HealerStart)>50 || FVector::Dist(MedicalPosition(Character),PatientStart)>50))
    { Error=TEXT("Treatment interrupted by movement — supply retained");return false; }
    if(FVector::Dist(Healer->GetActorLocation(),Character->GetActorLocation())>Tuning()->TreatmentRangeCm) { Error=TEXT("Patient out of reach"); return false; }
    FCollisionQueryParams Params; Params.AddIgnoredActor(Healer); Params.AddIgnoredActor(Character);
    FVector HealerEye,PatientEye; FRotator EyeRotation;
    Healer->GetActorEyesViewPoint(HealerEye,EyeRotation);
    Character->GetActorEyesViewPoint(PatientEye,EyeRotation);
    FHitResult VisibilityHit;
    const bool bObstructed=GetWorld()->LineTraceSingleByChannel(VisibilityHit,HealerEye,PatientEye,ECC_Visibility,Params);
    if(DebugAllowed() && MedicalDebug.GetValueOnGameThread())
    {
        FHitResult LegacyHit;
        GetWorld()->LineTraceSingleByChannel(LegacyHit,Healer->GetActorLocation(),Character->GetActorLocation(),ECC_Visibility,Params);
        UE_LOG(LogRVNetworking,Log,TEXT("Medical visibility center=%s eye=%s"),*GetNameSafe(LegacyHit.GetComponent()),*GetNameSafe(VisibilityHit.GetComponent()));
    }
    if(bObstructed) { Error=TEXT("Patient obstructed"); return false; }
    const auto* Inventory=Healer->FindComponentByClass<URVInventoryComponent>(); if(!Inventory) return false;
    const auto Items=Inventory->GetItems(); const auto* Item=Items.FindByPredicate([&](const auto& I){return I.Id==SupplyId;});
    if(!Item || !Item->Definition || !Item->Definition->Medical.bMedicalSupply || Item->Quantity<1 || Item->Condition<Item->Definition->Medical.MinimumCondition) { Error=TEXT("Medical supply unavailable"); return false; }
    const auto& M=Item->Definition->Medical;
    if(!FMath::IsFinite(M.DurationSeconds) || M.DurationSeconds<=0 || !FMath::IsFinite(M.MinimumCondition) || !FMath::IsFinite(M.MaximumSeverity) || !FMath::IsFinite(M.BleedingReduction) || !FMath::IsFinite(M.MedicationSeconds) || M.MedicationSeconds<=0 || !FMath::IsFinite(M.PainRelief))
    { Error=TEXT("Medical supply configuration invalid" ); return false; }
    const auto* PC=Cast<ARVPlayerController>(PS->GetOwner());
    if(M.bRequiresStation && (!PC || !PC->MedicalStation || !PC->MedicalStation->IsReachable(Healer) || !PC->MedicalStation->CanInteract_Implementation(Healer)))
    { Error=TEXT("Use a reachable medical station"); return false; }
    if(M.bRequiresParked)
    {
        const AActor* Vehicle=PC && PC->MedicalStation?PC->MedicalStation->GetAttachParentActor():nullptr;
        if(!Vehicle || Vehicle->GetVelocity().Size()>30) { Error=TEXT("Park the RV for this treatment"); return false; }
    }
    if(M.Treatment==ERVTreatmentKind::Revive)
    {
        if(Health==this || Health->LifeState!=ERVMedicalLifeState::Downed) { Error=TEXT("Patient is not revivable"); return false; }
        if(Health->Injuries.ContainsByPredicate([](const auto& I){return I.BleedingPerMinute>0;}))
        { Error=TEXT("Control bleeding before reviving");return false; }
        return true;
    }
    const auto* I=Health->Injuries.FindByPredicate([&](const auto& Entry){return Entry.Id==ActiveTreatment;});
    if(!I || I->Revision!=InjuryRevision || I->Severity>M.MaximumSeverity || I->Healing>=1) { Error=TEXT("Injury changed or inappropriate supply"); return false; }
    bool Valid=false;
    switch(M.Treatment)
    {
    case ERVTreatmentKind::Bandage: case ERVTreatmentKind::PressureDressing: Valid=I->Kind==ERVInjuryKind::Wound && I->BleedingPerMinute>0; break;
    case ERVTreatmentKind::Antiseptic: Valid=I->InfectionRisk>0; break;
    case ERVTreatmentKind::Splint: Valid=I->Kind==ERVInjuryKind::Fracture && !I->bStabilized; break;
    case ERVTreatmentKind::BurnDressing: Valid=I->Kind==ERVInjuryKind::Burn && !I->bTreated; break;
    case ERVTreatmentKind::Analgesic: Valid=Health->GetPain()>0; break;
    default: break;
    }
    if(!Valid) Error=TEXT("Treatment does not match injury"); return Valid;
}
void URVHealthComponent::CompleteTreatment()
{
    FString Error; if(!ValidateTreatment(Error)) { CancelTreatment(Error); return; }
    auto* PS=Cast<ARVPlayerState>(GetOwner()); auto* Patient=TreatmentPatient.Get(); auto* Health=Patient->Health.Get();
    auto* Inventory=PS->Needs->ResolveSurvivor()->FindComponentByClass<URVInventoryComponent>();
    FRVItemInstance Consumed;
    if(!Inventory->ConsumeOneAuthority(SupplyId,Consumed,Error)) { CancelTreatment(Error); return; }
    const auto& M=Consumed.Definition->Medical;
    if(M.Treatment==ERVTreatmentKind::Analgesic)
    {
        auto* ASC=Patient->MedicalAbilitySystem.Get();
        // Re-dose refreshes one native effect instead of accumulating unbounded relief.
        ASC->RemoveActiveGameplayEffectBySourceEffect(URVAnalgesicEffect::StaticClass(),ASC);
        auto Spec=ASC->MakeOutgoingSpec(URVAnalgesicEffect::StaticClass(),1,ASC->MakeEffectContext());
        if(Spec.IsValid())
        {
            Spec.Data->SetDuration(FMath::Max(.1f,M.MedicationSeconds),true);
            Spec.Data->SetSetByCallerMagnitude(FGameplayTag::RequestGameplayTag(TEXT("Medical.Medication.PainRelief")),FMath::Clamp(M.PainRelief,0.f,100.f));
            ASC->ApplyGameplayEffectSpecToSelf(*Spec.Data.Get());
        }
    }
    if(M.Treatment==ERVTreatmentKind::Revive)
    {
        Health->LifeState=ERVMedicalLifeState::Active; Health->DownedSeconds=0;
        Patient->MedicalAbilitySystem->SetNumericAttributeBase(URVMedicalAttributes::GetBloodAttribute(),FMath::Max(Patient->MedicalAttributes->GetBlood(),Tuning()->DownedBlood+5));
        Patient->MedicalAbilitySystem->SetNumericAttributeBase(URVMedicalAttributes::GetVitalityAttribute(),FMath::Max(Patient->MedicalAttributes->GetVitality(),15.f));
    }
    else if(auto* I=Health->Injuries.FindByPredicate([&](const auto& Entry){return Entry.Id==ActiveTreatment;}))
    {
        if(M.Treatment==ERVTreatmentKind::Bandage || M.Treatment==ERVTreatmentKind::PressureDressing) { I->BleedingPerMinute*=1-FMath::Clamp(M.BleedingReduction,0.f,1.f); I->bStabilized=I->BleedingPerMinute<=0; I->bTreated=true; }
        if(M.Treatment==ERVTreatmentKind::Antiseptic) { I->InfectionRisk=FMath::Max(0.f,I->InfectionRisk-.5f); I->bCleaned=true; }
        if(M.Treatment==ERVTreatmentKind::Splint || M.Treatment==ERVTreatmentKind::BurnDressing) { I->bStabilized=true; I->bTreated=true; }
        ++I->Revision;
    }
    Patient->ForceNetUpdate(); CancelTreatment(TEXT("Treatment completed"));
}
void URVHealthComponent::ServerCancelTreatment_Implementation() { if(GetOwner()->HasAuthority()) CancelTreatment(TEXT("Treatment cancelled — supply retained")); }
void URVHealthComponent::CancelTreatment(const FString& Reason)
{
    GetWorld()->GetTimerManager().ClearTimer(TreatmentTimer);
    if(auto* Patient=TreatmentPatient.Get(); Patient && Patient->Health && Patient->Health->ReservedBy.Get()==this) Patient->Health->ReservedBy.Reset();
    TreatmentPatient.Reset(); HealerFrame.Reset();PatientFrame.Reset();ActiveTreatment.Invalidate(); SupplyId.Invalidate(); TreatmentEndTime=0; Feedback=Reason;
    GetOwner()->ForceNetUpdate();
}
