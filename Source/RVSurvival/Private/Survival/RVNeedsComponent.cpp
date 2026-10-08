#include "Survival/RVNeedsComponent.h"
#include "Medical/RVHealthComponent.h"
#include "Survival/RVRestPoint.h"
#include "Survival/RVRestPoseComponent.h"
#include "Player/RVPlayerState.h"
#include "Player/RVPlayerController.h"
#include "Player/RVSurvivorCharacter.h"
#include "Vehicles/RVVehicleBase.h"
#include "Vehicles/RVVehicleSeatComponent.h"
#include "Inventory/RVInventoryComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Net/UnrealNetwork.h"
#include "TimerManager.h"
#include "HAL/IConsoleManager.h"
#include "NativeGameplayTags.h"
#include "Misc/ScopeExit.h"
UE_DEFINE_GAMEPLAY_TAG_STATIC(NeedsHungry,"Survival.Status.Hungry");
UE_DEFINE_GAMEPLAY_TAG_STATIC(NeedsDehydrated,"Survival.Status.Dehydrated");
UE_DEFINE_GAMEPLAY_TAG_STATIC(NeedsThirsty,"Survival.Status.Thirsty");
UE_DEFINE_GAMEPLAY_TAG_STATIC(NeedsVeryHungry,"Survival.Status.VeryHungry");
UE_DEFINE_GAMEPLAY_TAG_STATIC(NeedsTired,"Survival.Status.Tired");
UE_DEFINE_GAMEPLAY_TAG_STATIC(NeedsExhausted,"Survival.Status.Exhausted");
UE_DEFINE_GAMEPLAY_TAG_STATIC(NeedsResting,"Survival.Status.Resting");
UE_DEFINE_GAMEPLAY_TAG_STATIC(NeedsSleeping,"Survival.Status.Sleeping");
void URVNeedsComponent::OnRep_State() { OnNeedsChanged.Broadcast(); }
FGameplayTagContainer URVNeedsComponent::GetStatusTags() const
{
    FGameplayTagContainer Tags;
    if(State.Nutrition<=Tuning.NutritionWarning) Tags.AddTag(State.Nutrition<=Tuning.NutritionCritical?NeedsVeryHungry:NeedsHungry);
    if(State.Hydration<=Tuning.HydrationWarning) Tags.AddTag(State.Hydration<=Tuning.HydrationCritical?NeedsDehydrated:NeedsThirsty);
    if(State.Fatigue>=Tuning.FatigueWarning) Tags.AddTag(State.Fatigue>=Tuning.FatigueCritical?NeedsExhausted:NeedsTired);
    if(State.RestMode!=ERVRestMode::Awake) Tags.AddTag(State.RestMode==ERVRestMode::Sleeping?NeedsSleeping:NeedsResting);
    return Tags;
}

static TAutoConsoleVariable<int32> NeedsDebug(TEXT("rv.Needs.AllowDebug"),0,TEXT("Enable non-shipping authoritative needs test controls"));
URVNeedsComponent::URVNeedsComponent()
{
    SetIsReplicatedByDefault(true);
    PrimaryComponentTick.bCanEverTick=true;
    PrimaryComponentTick.TickInterval=.25f;
}
void URVNeedsComponent::BeginPlay()
{
    Super::BeginPlay();
    if(GetOwner()->HasAuthority())
    {
        if(TuningAsset) Tuning=TuningAsset->Values;
        Tuning.Maximum=FMath::IsFinite(Tuning.Maximum)?FMath::Max(1.f,Tuning.Maximum):100.f;
        if(!bCopiedPersistentState)
        {
            State.Nutrition=FMath::Clamp(Tuning.StartingNutrition,0.f,Tuning.Maximum);
            State.Hydration=FMath::Clamp(Tuning.StartingHydration,0.f,Tuning.Maximum);
            State.Fatigue=FMath::Clamp(Tuning.StartingFatigue,0.f,Tuning.Maximum);
            State.SurvivalReserve=Tuning.Maximum;
        }
    }
}
void URVNeedsComponent::EndPlay(const EEndPlayReason::Type Reason)
{ EndRestAuthority(true); Super::EndPlay(Reason); }
void URVNeedsComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(URVNeedsComponent,Tuning);
    DOREPLIFETIME(URVNeedsComponent,State);
    DOREPLIFETIME(URVNeedsComponent,RestLocation);
    DOREPLIFETIME_CONDITION(URVNeedsComponent,Feedback,COND_OwnerOnly);
}
ARVSurvivorCharacter* URVNeedsComponent::ResolveSurvivor() const
{
    const auto* PS=Cast<ARVPlayerState>(GetOwner());
    const auto* PC=PS?Cast<ARVPlayerController>(PS->GetOwner()):nullptr;
    if(!PC) return nullptr;
    if(auto* Character=Cast<ARVSurvivorCharacter>(PC->GetPawn())) return Character;
    if(PC->SeatedVehicle)
        for(auto* Seat:PC->SeatedVehicle->GetSeats())
            if(Seat->OccupantController.Get()==PC) return Seat->Occupant;
    return nullptr;
}
float URVNeedsComponent::ActivityMultiplier() const
{
    if(State.RestMode==ERVRestMode::Sleeping) return FMath::Max(0.f,Tuning.SleepMetabolism);
    if(State.RestMode==ERVRestMode::Resting) return FMath::Max(0.f,Tuning.RestMetabolism);
    const auto* PS=Cast<ARVPlayerState>(GetOwner());
    const auto* PC=PS?Cast<ARVPlayerController>(PS->GetOwner()):nullptr;
    if(PC && PC->SeatedVehicle) return FMath::Max(0.f,PC->GetPawn()==PC->SeatedVehicle?Tuning.DrivingMultiplier:Tuning.PassengerMultiplier);
    const auto* Character=ResolveSurvivor();
    float Multiplier=Character && Character->GetCharacterMovement()->GetCurrentAcceleration().SizeSquared()>1 ? Tuning.WalkingMultiplier : 1;
    if(Character)
        if(const auto* Inventory=Character->FindComponentByClass<URVInventoryComponent>(); Inventory && Inventory->MaxWeightKg>0 && Inventory->GetWeightKg()/Inventory->MaxWeightKg>.75f)
            Multiplier*=Tuning.HeavyCarryMultiplier;
    return FMath::IsFinite(Multiplier)?FMath::Max(0.f,Multiplier):1;
}
void URVNeedsComponent::Advance(double Seconds)
{
    if(!GetOwner()->HasAuthority() || !FMath::IsFinite(Seconds) || Seconds<=0) return;
    const double Hours=Seconds/3600;
    const double Activity=ActivityMultiplier();
    const double NutritionRate=FMath::Max(0.f,Tuning.NutritionPerHour)*Activity;
    const double HydrationRate=FMath::Max(0.f,Tuning.HydrationPerHour)*Activity;
    // Integrate only the portion of this interval spent below a critical threshold.
    const auto CriticalHours=[Hours](double Before,double Rate,double Threshold)
    { return Before<=Threshold?Hours:(Rate>0?FMath::Max(0.,Hours-(Before-Threshold)/Rate):0.); };
    const double Damage=CriticalHours(State.Nutrition,NutritionRate,Tuning.NutritionCritical)*FMath::Max(0.f,Tuning.HungerReserveLossPerHour)
        +CriticalHours(State.Hydration,HydrationRate,Tuning.HydrationCritical)*FMath::Max(0.f,Tuning.ThirstReserveLossPerHour);
    State.Nutrition=FMath::Clamp(float(State.Nutrition-NutritionRate*Hours),0.f,Tuning.Maximum);
    State.Hydration=FMath::Clamp(float(State.Hydration-HydrationRate*Hours),0.f,Tuning.Maximum);
    double FatigueRate=FMath::Max(0.f,Tuning.FatiguePerHour)*Activity;
    if(State.RestMode==ERVRestMode::Resting) FatigueRate=-FMath::Max(0.f,Tuning.RestRecoveryPerHour);
    if(State.RestMode==ERVRestMode::Sleeping) FatigueRate=-FMath::Max(0.f,Tuning.SleepRecoveryPerHour);
    State.Fatigue=FMath::Clamp(float(State.Fatigue+FatigueRate*Hours),0.f,Tuning.Maximum);
    // Minimal replaceable consequence; no injury model or death in this gate.
    State.SurvivalReserve=FMath::Clamp(float(State.SurvivalReserve-Damage),1.f,Tuning.Maximum);
    State.SimulatedSeconds+=Seconds;
    OnRep_State();
}
void URVNeedsComponent::TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Function)
{
    Super::TickComponent(Delta,Type,Function);
    if(!GetOwner()->HasAuthority()) return;
    if(State.RestMode!=ERVRestMode::Awake && (!IsValid(RestLocation) || !RestingCharacter.IsValid() || ResolveSurvivor()!=RestingCharacter.Get() || RestingCharacter->SeatedVehicle || !RestLocation->CanContinueRest(RestingCharacter.Get())))
        EndRestAuthority();
    Advance(double(Delta)*DevelopmentTimeScale);
}
float URVNeedsComponent::GetMovementScale() const
{
    if(State.RestMode!=ERVRestMode::Awake) return 0;
    float Scale=1;
    if(State.Nutrition<=Tuning.NutritionCritical) Scale=FMath::Min(Scale,Tuning.HungrySpeedScale);
    if(State.Hydration<=Tuning.HydrationCritical) Scale=FMath::Min(Scale,Tuning.DehydratedSpeedScale);
    if(State.Fatigue>=Tuning.FatigueCritical) Scale=FMath::Min(Scale,Tuning.ExhaustedSpeedScale);
    return FMath::Clamp(Scale,0.f,1.f);
}
FString URVNeedsComponent::GetWarnings() const
{
    TArray<FString> Warnings;
    if(State.Nutrition<=Tuning.NutritionWarning) Warnings.Add(State.Nutrition<=Tuning.NutritionCritical?TEXT("Very hungry"):TEXT("Hungry"));
    if(State.Hydration<=Tuning.HydrationWarning) Warnings.Add(State.Hydration<=Tuning.HydrationCritical?TEXT("Dehydrated"):TEXT("Thirsty"));
    if(State.Fatigue>=Tuning.FatigueWarning) Warnings.Add(State.Fatigue>=Tuning.FatigueCritical?TEXT("Exhausted"):TEXT("Tired"));
    if(State.RestMode!=ERVRestMode::Awake) Warnings.Add(State.RestMode==ERVRestMode::Sleeping?TEXT("Sleeping | R / E: stand up | Z: rest"):TEXT("Resting | R / E: stand up | Z: sleep"));
    return FString::Join(Warnings,TEXT(" | "));
}
void URVNeedsComponent::RequestConsume(FGuid Id)
{
    const auto* PC=Cast<APlayerController>(GetOwner()->GetOwner());
    if(!PC || !PC->IsLocalController()) return;
    GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Id]{ServerConsume(Id);}));
}
void URVNeedsComponent::RequestRestMode(ERVRestMode Mode)
{
    const auto* PC=Cast<APlayerController>(GetOwner()->GetOwner());
    if(!PC || !PC->IsLocalController()) return;
    GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Mode]{ServerRestMode(Mode);}));
}
void URVNeedsComponent::ServerConsume_Implementation(FGuid Id)
{
    if(!GetOwner()->HasAuthority()) return;
    if(const auto* PS=Cast<ARVPlayerState>(GetOwner());PS && !PS->Health->CanAct()) { Feedback=TEXT("Cannot consume while downed");return; }
    ON_SCOPE_EXIT { OnRep_State(); GetOwner()->ForceNetUpdate(); };
    auto* Character=ResolveSurvivor();
    auto* Inventory=Character?Character->FindComponentByClass<URVInventoryComponent>():nullptr;
    if(!Inventory) return;
    Feedback.Empty();
    const auto Items=Inventory->GetItems();
    const auto* Item=Items.FindByPredicate([&](const auto& I){return I.Id==Id;});
    if(!Item || !Item->Definition) { Feedback=TEXT("Item no longer owned"); return; }
    const auto Metadata=Item->Definition->Consumable;
    if(!Metadata.bConsumable || !FMath::IsFinite(Metadata.Nutrition) || !FMath::IsFinite(Metadata.Hydration) || Metadata.Nutrition<0 || Metadata.Hydration<0 || !FMath::IsFinite(Metadata.MinimumCondition) || Item->Condition<Metadata.MinimumCondition)
    { Feedback=TEXT("Item cannot be consumed"); return; }
    if((Metadata.Nutrition<=0 || State.Nutrition>=Tuning.Maximum) && (Metadata.Hydration<=0 || State.Hydration>=Tuning.Maximum))
    { Feedback=TEXT("No need for this consumable"); return; }
    if(GetWorld()->GetTimeSeconds()<NextConsumptionTime) { Feedback=TEXT("Wait before consuming again"); return; }
    FRVItemInstance Consumed;
    if(!Inventory->ConsumeOneAuthority(Id,Consumed,Feedback)) return;
    State.Nutrition=FMath::Clamp(State.Nutrition+Metadata.Nutrition,0.f,Tuning.Maximum);
    State.Hydration=FMath::Clamp(State.Hydration+Metadata.Hydration,0.f,Tuning.Maximum);
    NextConsumptionTime=GetWorld()->GetTimeSeconds()+.25;
    Feedback=FString::Printf(TEXT("Consumed %s"),*Consumed.Definition->DisplayName.ToString());
    OnRep_State();
    GetOwner()->ForceNetUpdate();
}
bool URVNeedsComponent::BeginRestAuthority(ARVRestPoint* Point,ARVSurvivorCharacter* Character)
{
    if(!GetOwner()->HasAuthority() || !Point || Character!=ResolveSurvivor() || !Point->CanContinueRest(Character) || Point->Occupant || Character->SeatedVehicle) return false;
    EndRestAuthority();
    if (State.RestMode!=ERVRestMode::Awake) return false;
    if (Point->bUseLyingPose)
    {
        auto* Pose=Character->FindComponentByClass<URVRestPoseComponent>();
        if (!Pose || !Pose->BeginPoseAuthority(Point)) { Feedback=TEXT("Bed or stand-up aisle is obstructed."); GetOwner()->ForceNetUpdate(); return false; }
    }
    Point->Occupant=Cast<ARVPlayerState>(GetOwner()); Point->ForceNetUpdate();
    RestLocation=Point; RestingCharacter=Character; State.RestMode=ERVRestMode::Resting;
    Character->GetCharacterMovement()->StopMovementImmediately();
    OnRep_State();
    Feedback=Point->DisplayName.ToString(); GetOwner()->ForceNetUpdate(); return true;
}
void URVNeedsComponent::EndRestAuthority(bool bForceCleanup)
{
    if(!GetOwner() || !GetOwner()->HasAuthority()) return;
    if (RestingCharacter.IsValid())
        if (auto* Pose=RestingCharacter->FindComponentByClass<URVRestPoseComponent>(); Pose && !Pose->EndPoseAuthority(bForceCleanup))
        { Feedback=TEXT("Stand-up aisle occupied. R: retry standing up."); GetOwner()->ForceNetUpdate(); return; }
    if(IsValid(RestLocation)) RestLocation->ReleaseAuthority(Cast<ARVPlayerState>(GetOwner()));
    RestLocation=nullptr; RestingCharacter.Reset(); State.RestMode=ERVRestMode::Awake; GetOwner()->ForceNetUpdate();
    OnRep_State();
}
void URVNeedsComponent::ServerRestMode_Implementation(ERVRestMode Mode)
{
    if(!GetOwner()->HasAuthority()) return;
    if (DebugAllowed()) UE_LOG(LogTemp,Log,TEXT("RVRest request=%d before=%d point=%s character=%s valid=%d"),int32(Mode),int32(State.RestMode),*GetNameSafe(RestLocation),*GetNameSafe(RestingCharacter.Get()),IsValid(RestLocation)&&RestLocation->CanContinueRest(RestingCharacter.Get()));
    ON_SCOPE_EXIT { OnRep_State(); GetOwner()->ForceNetUpdate(); };
    if(Mode==ERVRestMode::Awake) { EndRestAuthority(); if(State.RestMode==ERVRestMode::Awake) Feedback=TEXT("Awake"); return; }
    if((Mode!=ERVRestMode::Resting && Mode!=ERVRestMode::Sleeping) || !IsValid(RestLocation) || !RestLocation->CanContinueRest(RestingCharacter.Get())) return;
    State.RestMode=Mode; OnRep_State(); GetOwner()->ForceNetUpdate();
}
bool URVNeedsComponent::DebugAllowed() const
{
#if !(UE_BUILD_SHIPPING || UE_BUILD_TEST)
    return GetOwner() && GetOwner()->HasAuthority() && NeedsDebug.GetValueOnGameThread()!=0;
#else
    return false;
#endif
}
bool URVNeedsComponent::DebugSetValues(float Nutrition,float Hydration,float Fatigue)
{
    if(!DebugAllowed() || !FMath::IsFinite(Nutrition) || !FMath::IsFinite(Hydration) || !FMath::IsFinite(Fatigue)) return false;
    State.Nutrition=FMath::Clamp(Nutrition,0.f,Tuning.Maximum); State.Hydration=FMath::Clamp(Hydration,0.f,Tuning.Maximum); State.Fatigue=FMath::Clamp(Fatigue,0.f,Tuning.Maximum); OnRep_State(); GetOwner()->ForceNetUpdate(); return true;
}
bool URVNeedsComponent::DebugSetTimeScale(float Scale)
{ if(!DebugAllowed() || !FMath::IsFinite(Scale) || Scale<0 || Scale>10000) return false; DevelopmentTimeScale=Scale; return true; }
bool URVNeedsComponent::DebugAdvanceTime(float Seconds)
{ if(!DebugAllowed() || !FMath::IsFinite(Seconds) || Seconds<0 || Seconds>86400*30) return false; Advance(Seconds); GetOwner()->ForceNetUpdate(); return true; }
void URVNeedsComponent::CopyPersistentValuesTo(URVNeedsComponent* Destination) const
{ if(GetOwner()->HasAuthority() && Destination && Destination->GetOwner()->HasAuthority()) { Destination->Tuning=Tuning; Destination->State=State; Destination->State.RestMode=ERVRestMode::Awake; Destination->bCopiedPersistentState=true; } }
