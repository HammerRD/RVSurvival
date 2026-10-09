#include "Combat/RVCombatComponent.h"
#include "Combat/RVInfected.h"
#include "Combat/RVWeaponPresentationProfile.h"
#include "Combat/RVBodyRegionHitComponent.h"
#include "Player/RVCharacterVisualProfile.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVPlayerState.h"
#include "Player/RVInputMappings.h"
#include "Player/RVCharacterPresentationComponent.h"
#include "Player/RVLadderClimbComponent.h"
#include "Medical/RVHealthComponent.h"
#include "Survival/RVNeedsComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Camera/CameraModifier_CameraShake.h"
#include "Shakes/DefaultCameraShakeBase.h"
#include "Shakes/WaveOscillatorCameraShakePattern.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputAction.h"
#include "InputMappingContext.h"
#include "Engine/LocalPlayer.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/GameStateBase.h"
#include "Kismet/GameplayStatics.h"
#include "Perception/AISense_Hearing.h"
#include "Net/UnrealNetwork.h"
#include "TimerManager.h"
#include "DrawDebugHelpers.h"
#include "HAL/IConsoleManager.h"
#include "NativeGameplayTags.h"
#include "Animation/AnimMontage.h"
#include "Engine/StaticMeshActor.h"
#include "Components/PointLightComponent.h"
UE_DEFINE_GAMEPLAY_TAG_STATIC(TAG_RV9mm,"Item.Ammo.9mm");
UE_DEFINE_GAMEPLAY_TAG_STATIC(TAG_RV45ACP,"Item.Ammo.45ACP");
static TAutoConsoleVariable<int32> CombatDebugTrace(TEXT("rv.Combat.DebugTrace"),0,TEXT("Development-only shot trace overlay"));

URVCombatComponent::URVCombatComponent(){SetIsReplicatedByDefault(true);PrimaryComponentTick.bCanEverTick=true;}
URVInventoryComponent* URVCombatComponent::Inventory() const{return GetOwner()->FindComponentByClass<URVInventoryComponent>();}
bool URVCombatComponent::GetWeapon(FRVItemInstance& Item) const
{if(const auto* I=Inventory())for(const auto& W:I->GetItems())if(W.Id==EquippedWeapon){Item=W;return W.Definition && (W.Definition->Combat.bFirearm || W.Definition->Combat.bMelee || W.Definition->Combat.bQuickAccess);}return false;}
int32 URVCombatComponent::GetLoadedRounds() const
{if(const auto* I=Inventory())for(const auto& M:I->GetItems())if(EquippedWeapon.IsValid() && M.LoadedInWeapon==EquippedWeapon)return M.MagazineRounds;return 0;}
bool URVCombatComponent::CanUse() const
{
    const auto* C=Cast<ARVSurvivorCharacter>(GetOwner());if(!bEnabled || !C || !C->GetController() || C->SeatedVehicle)return false;
    const auto* PS=C->GetPlayerState<ARVPlayerState>();if(!PS || !PS->Health->CanAct() || PS->Health->ActiveTreatment.IsValid() || PS->Needs->State.RestMode!=ERVRestMode::Awake)return false;
    const auto* L=C->FindComponentByClass<URVLadderClimbComponent>();return !L || !L->Ladder;
}
void URVCombatComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(URVCombatComponent,EquippedWeapon);DOREPLIFETIME(URVCombatComponent,bAiming);DOREPLIFETIME(URVCombatComponent,ReloadEnds);DOREPLIFETIME(URVCombatComponent,ShotSequence);DOREPLIFETIME(URVCombatComponent,MeleeSequence);DOREPLIFETIME_CONDITION(URVCombatComponent,Feedback,COND_OwnerOnly);}
void URVCombatComponent::ServerEquip_Implementation(FGuid Id)
{
    if(!GetOwner()->HasAuthority())return;
    if(!CanUse()){Feedback=TEXT("Cannot equip in this state");return;}
    if(Id.IsValid())
    {bool Owned=false;for(const auto& W:Inventory()->GetItems())if(W.Id==Id && W.Definition && (W.Definition->Combat.bFirearm || W.Definition->Combat.bMelee || W.Definition->Combat.bQuickAccess) && W.Definition->bEquippable)Owned=true;
     if(!Owned){Feedback=TEXT("Weapon not owned");return;}}
    if(GetWorld()->GetTimerManager().IsTimerActive(MeleeHitTimer)){Feedback=TEXT("Finish the swing before switching");return;}
    if(auto* C=Cast<ACharacter>(GetOwner()))C->StopAnimMontage();
    CancelReload(); // Holstering preserves the magazine physically loaded in this owned gun.
    EquippedWeapon=Id;bAiming=false;Feedback.Empty();GetOwner()->ForceNetUpdate();
}
void URVCombatComponent::ServerAim_Implementation(bool Value){if(!GetOwner()->HasAuthority())return;FRVItemInstance W;bAiming=Value && CanUse() && GetWeapon(W) && W.Definition->Combat.bFirearm;GetOwner()->ForceNetUpdate();}
void URVCombatComponent::ServerFire_Implementation(FGuid Weapon,int32 Revision,uint32 Request)
{
    if(!GetOwner()->HasAuthority())return;
    if(Request==0 || Request<=LastRequest)return;
    FRVItemInstance W;
    if(!CanUse() || ReloadEnds>0 || Weapon!=EquippedWeapon || !GetWeapon(W) || !W.Definition->Combat.bFirearm){Feedback=TEXT("Cannot fire in this state");return;}
    const auto& C=W.Definition->Combat;const double Now=GetWorld()->GetTimeSeconds();
    if(!FMath::IsFinite(C.ShotInterval) || C.ShotInterval<.1f || !FMath::IsFinite(C.RangeCm) || C.RangeCm<1 || !FMath::IsFinite(C.Damage) || C.Damage<0)return;
    if(Now<NextShotTime){Feedback=TEXT("Weapon cycling");return;}
    if(!Inventory()->FireMagazineAuthority(Weapon,Revision,W,Feedback))return;
    LastRequest=Request;
    NextShotTime=Now+C.ShotInterval;++ShotSequence;
    auto* Pawn=Cast<APawn>(GetOwner());FVector Eye;FRotator Rotation;Pawn->GetActorEyesViewPoint(Eye,Rotation);
    FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(RVFirearm),true,GetOwner());
    const FVector End=Eye+Rotation.Vector()*C.RangeCm;
    GetWorld()->LineTraceSingleByChannel(Hit,Eye,End,ECC_Visibility,Params);
    if(Hit.GetActor() && (bFriendlyFire || !Cast<ARVSurvivorCharacter>(Hit.GetActor())))
        UGameplayStatics::ApplyPointDamage(Hit.GetActor(),C.Damage,Rotation.Vector(),Hit,Pawn->GetController(),Pawn,nullptr);
    UAISense_Hearing::ReportNoiseEvent(GetWorld(),Eye,1.f,Pawn,C.HearingRange,TEXT("Gunshot"));
    MulticastShot(Eye,Hit.bBlockingHit?Hit.ImpactPoint:End);GetOwner()->ForceNetUpdate();
}
void URVCombatComponent::ServerReload_Implementation(FGuid Magazine,int32 Revision)
{
    if(!GetOwner()->HasAuthority())return;
    FRVItemInstance W;if(!CanUse() || ReloadEnds>0 || !GetWeapon(W) || !W.Definition->Combat.bFirearm || W.CombatRevision!=Revision){Feedback=TEXT("Cannot reload stale weapon");return;}
    bool Valid=false;for(const auto& M:Inventory()->GetItems())if(M.Id==Magazine && M.Definition && M.Definition->Combat.bMagazine
        && !M.LoadedInWeapon.IsValid() && M.Definition->Combat.Caliber==W.Definition->Combat.Caliber && M.Condition>0)Valid=true;
    if(!Valid || !FMath::IsFinite(W.Definition->Combat.ReloadSeconds) || W.Definition->Combat.ReloadSeconds<.1f){Feedback=TEXT("Compatible spare magazine required");return;}
    ReloadMagazine=Magazine;ReloadRevision=Revision;
    const auto* GS=GetWorld()->GetGameState();ReloadEnds=(GS?GS->GetServerWorldTimeSeconds():GetWorld()->GetTimeSeconds())+W.Definition->Combat.ReloadSeconds;
    GetWorld()->GetTimerManager().SetTimer(ReloadTimer,this,&ThisClass::FinishReload,W.Definition->Combat.ReloadSeconds,false);GetOwner()->ForceNetUpdate();
}
void URVCombatComponent::FinishReload()
{if(CanUse())Inventory()->SwapMagazineAuthority(EquippedWeapon,ReloadMagazine,ReloadRevision,Feedback);else Feedback=TEXT("Reload interrupted");CancelReload();GetOwner()->ForceNetUpdate();}
void URVCombatComponent::CancelReload(){GetWorld()->GetTimerManager().ClearTimer(ReloadTimer);ReloadEnds=0;ReloadMagazine.Invalidate();}
void URVCombatComponent::ServerUnload_Implementation()
{if(!GetOwner()->HasAuthority())return;if(!CanUse() || ReloadEnds>0){Feedback=TEXT("Cannot unload in this state");return;}
 Inventory()->ReleaseMagazineAuthority(EquippedWeapon);Feedback=TEXT("Magazine removed to inventory");GetOwner()->ForceNetUpdate();}
void URVCombatComponent::MulticastShot_Implementation(FVector_NetQuantize Start,FVector_NetQuantize End)
{
    FRVItemInstance W;if(GetWeapon(W) && W.Definition->Combat.ShotSound)UGameplayStatics::PlaySoundAtLocation(this,W.Definition->Combat.ShotSound,Start);
    if(GetWeapon(W))if(auto* C=Cast<ACharacter>(GetOwner());C && W.Definition->Combat.FireMontage)C->PlayAnimMontage(W.Definition->Combat.FireMontage);
    if(GetWeapon(W) && W.Definition->Combat.ShotEffectMaterial)
    {
        auto Effect=[&](FVector Position,float Scale,float Seconds,bool Light)
        {
            FActorSpawnParameters Params;Params.ObjectFlags|=RF_Transient;
            auto* A=GetWorld()->SpawnActor<AStaticMeshActor>(Position,FRotator::ZeroRotator,Params);if(!A)return;
            auto* M=A->GetStaticMeshComponent();M->SetMobility(EComponentMobility::Movable);M->SetCollisionEnabled(ECollisionEnabled::NoCollision);
            M->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Sphere.Sphere")));M->SetMaterial(0,W.Definition->Combat.ShotEffectMaterial);
            A->SetActorScale3D(FVector(Scale));A->SetLifeSpan(Seconds);
            if(Light){auto* L=NewObject<UPointLightComponent>(A);L->SetupAttachment(M);L->SetIntensity(18000);L->SetAttenuationRadius(150);L->SetCastShadows(false);L->RegisterComponent();
                if(WeaponVisual)A->AttachToComponent(WeaponVisual,FAttachmentTransformRules::KeepWorldTransform);}
        };
        const auto& Alignment=W.Definition->Combat;
        const FVector Muzzle=WeaponVisual?(WeaponVisual->DoesSocketExist(Alignment.MuzzleSocket)?WeaponVisual->GetSocketLocation(Alignment.MuzzleSocket):WeaponVisual->GetComponentTransform().TransformPosition(Alignment.MuzzleTransform.GetLocation())):FVector(Start);
        Effect(Muzzle,.035f,.08f,true);Effect(End,.025f,.5f,false);
    }
    // Bounded prototype effect. Cosmetic loss never repeats an authoritative shot.
    #if !(UE_BUILD_SHIPPING || UE_BUILD_TEST)
    if(CombatDebugTrace.GetValueOnGameThread())
    {DrawDebugLine(GetWorld(),Start,End,FColor::Yellow,false,.08f,0,.7f);DrawDebugPoint(GetWorld(),End,5,FColor::Orange,false,.3f);}
#endif
    if(auto* P=Cast<APawn>(GetOwner());P && P->IsLocallyControlled())if(auto* PC=Cast<APlayerController>(P->GetController());PC && PC->PlayerCameraManager && GetWeapon(W))
    {
        const auto& Tuning=W.Definition->Combat;
        const float Pitch=FMath::Clamp(Tuning.RecoilPitch,0.f,3.f),Yaw=FMath::Clamp(Tuning.RecoilYaw,0.f,1.f);
        const float Recovery=FMath::Clamp(Tuning.RecoilRecoverySeconds,.05f,.5f);
        if(!FMath::IsFinite(Pitch) || !FMath::IsFinite(Yaw) || !FMath::IsFinite(Recovery))return;
        FAddCameraShakeParams Params;
        // Native camera manager owns timing/blending/cleanup. Only scalar tuning is
        // captured; recoil never changes the authoritative trace or ControlRotation.
        Params.Initializer=FOnInitializeCameraShake::CreateLambda([Pitch,Yaw,Recovery](UCameraShakeBase* Shake)
        {
            auto* Wave=NewObject<UWaveOscillatorCameraShakePattern>(Shake);
            Wave->Duration=Recovery;Wave->BlendInTime=.01f;Wave->BlendOutTime=Recovery*.8f;
            Wave->LocationAmplitudeMultiplier=0;Wave->RotationAmplitudeMultiplier=1;Wave->Roll.Amplitude=0;Wave->FOV.Amplitude=0;
            Wave->Pitch.Amplitude=Pitch;Wave->Pitch.Frequency=.8f/Recovery;Wave->Pitch.InitialOffsetType=EInitialWaveOscillatorOffsetType::Zero;
            Wave->Yaw.Amplitude=Yaw;Wave->Yaw.Frequency=.8f/Recovery;Wave->Yaw.InitialOffsetType=EInitialWaveOscillatorOffsetType::Random;
            Shake->SetRootShakePattern(Wave);
        });
        PC->PlayerCameraManager->StartCameraShake(UDefaultCameraShakeBase::StaticClass(),Params);
    }
}
void URVCombatComponent::UpdateVisual()
{
    auto* C=Cast<ACharacter>(GetOwner());if(!C)return;FRVItemInstance W;
    auto* D=GetWeapon(W)?W.Definition.Get():nullptr;
    if(!WeaponVisual){WeaponVisual=NewObject<UStaticMeshComponent>(GetOwner(),TEXT("EquippedFirearmVisual"));WeaponVisual->SetCollisionEnabled(ECollisionEnabled::NoCollision);WeaponVisual->RegisterComponent();}
    if(D!=VisualDefinition){C->StopAnimMontage();VisualDefinition=D;WeaponVisual->SetStaticMesh(D?D->WorldMesh.LoadSynchronous():nullptr);
        if(D)if(auto* P=C->FindComponentByClass<URVCharacterPresentationComponent>())if(auto* A=P->GetEquipmentAnchor(D->Combat.HandAnchor))
        {WeaponVisual->AttachToComponent(A,FAttachmentTransformRules::SnapToTargetNotIncludingScale);WeaponVisual->SetRelativeTransform(D->Combat.GripOffset);}}
    const auto* PS=C->GetPlayerState<ARVPlayerState>();
    const auto* Survivor=Cast<ARVSurvivorCharacter>(C);
    const auto* Climb=C->FindComponentByClass<URVLadderClimbComponent>();
    WeaponVisual->SetVisibility(D && bEnabled && PS && PS->Health->CanAct() && !PS->Health->ActiveTreatment.IsValid()
        && PS->Needs->State.RestMode==ERVRestMode::Awake && (!Climb || !Climb->Ladder) && (!Survivor || !Survivor->SeatedVehicle));
    // Holstering removes the definition, but must still release the owner's ADS
    // camera. Do not leave the previous weapon's zoom active without a weapon.
    if(!D && C->IsLocallyControlled())
    {
        AimBlend=0;
        if(bLocalAimApplied)if(auto* Camera=C->FindComponentByClass<UCameraComponent>())
        {
            Camera->SetFieldOfView(FMath::FInterpTo(Camera->FieldOfView,UnaimedFOV,GetWorld()->GetDeltaSeconds(),12.f));
            if(FMath::IsNearlyEqual(Camera->FieldOfView,UnaimedFOV,.01f))
            {Camera->SetFieldOfView(UnaimedFOV);bLocalAimApplied=false;}
        }
    }
    if(ReloadEnds!=PresentedReloadEnd)
    {PresentedReloadEnd=ReloadEnds;if(D && D->Combat.ReloadMontage)
      {if(ReloadEnds>0){const auto* GS=GetWorld()->GetGameState();const float Remaining=ReloadEnds-(GS?GS->GetServerWorldTimeSeconds():GetWorld()->GetTimeSeconds());
        if(Remaining>.05f)C->PlayAnimMontage(D->Combat.ReloadMontage,D->Combat.ReloadMontage->GetPlayLength()/Remaining);}
       else C->StopAnimMontage(D->Combat.ReloadMontage);}}
    if(D)if(auto* P=C->FindComponentByClass<URVCharacterPresentationComponent>())if(auto* Anchor=P->GetEquipmentAnchor(D->Combat.HandAnchor))
    {
        const auto& A=D->Combat;
        const auto* Family=A.Presentation.Get();
        const FTransform FamilyOffset=Family?(C->IsLocallyControlled()?Family->FirstPersonOffset:Family->ThirdPersonOffset):FTransform::Identity;
        WeaponVisual->SetRelativeTransform(A.GripOffset*(C->IsLocallyControlled()?A.FirstPersonOffset:A.ThirdPersonOffset)*FamilyOffset);
        if(C->IsLocallyControlled())if(auto* Camera=C->FindComponentByClass<UCameraComponent>())
        {
            const bool Aim=bAiming && CanUse() && A.bFirearm && ReloadEnds<=0;
            if(Aim && !bLocalAimApplied)UnaimedFOV=Camera->FieldOfView;
            AimBlend=FMath::FInterpTo(AimBlend,Aim?1.f:0.f,GetWorld()->GetDeltaSeconds(),A.AimBlendSpeed);
            if(Aim || bLocalAimApplied || AimBlend>.001f)Camera->SetFieldOfView(FMath::Lerp(UnaimedFOV,UnaimedFOV*(A.bSightADS?A.SightFOVScale:AimFOVScale),AimBlend));
            bLocalAimApplied=Aim || AimBlend>.001f;
        }

    }
}
void URVCombatComponent::TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Function)
{
    Super::TickComponent(Delta,Type,Function);
    if(!bEnabled)return;
    if(!bHitQueriesConfigured)if(auto* C=Cast<ACharacter>(GetOwner());C && C->GetMesh()->GetSkeletalMeshAsset())
    {C->GetMesh()->SetCollisionEnabled(ECollisionEnabled::QueryOnly);C->GetMesh()->SetCollisionResponseToAllChannels(ECR_Ignore);
     C->GetMesh()->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);C->GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility,ECR_Ignore);
     if(auto* V=C->FindComponentByClass<URVCharacterPresentationComponent>();V && V->Profile)
     for(const auto& R:V->Profile->BodyRegions)if(R.QueryRadiusCm>0 && C->GetMesh()->DoesSocketExist(R.AnchorBone))
     {auto* Q=NewObject<URVBodyRegionHitComponent>(C);Q->Region=R.Region;Q->SetupAttachment(C->GetMesh(),R.AnchorBone);Q->SetAbsolute(false,false,true);Q->InitSphereRadius(R.QueryRadiusCm);
      Q->SetCollisionEnabled(ECollisionEnabled::QueryOnly);Q->SetCollisionResponseToAllChannels(ECR_Ignore);Q->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);Q->RegisterComponent();HitQueries.Add(Q);}
     bHitQueriesConfigured=true;}
    if(GetOwner()->HasAuthority())
    {if(!CanUse()){bAiming=false;if(ReloadEnds>0)CancelReload();}FRVItemInstance W;if(EquippedWeapon.IsValid() && !GetWeapon(W)){CancelReload();Inventory()->ReleaseMagazineAuthority(EquippedWeapon);EquippedWeapon.Invalidate();}}
    UpdateVisual();
}
void URVCombatComponent::BindInput(UEnhancedInputComponent* Input)
{
    if(!bEnabled)return;
    auto* P=Cast<APawn>(GetOwner());auto* PC=P?Cast<APlayerController>(P->GetController()):nullptr;if(!PC)return;
    if(!Mapping){Mapping=NewObject<UInputMappingContext>(this);
        auto Make=[&](TObjectPtr<UInputAction>& A,FKey Key,FName Name,const TCHAR* Label){A=NewObject<UInputAction>(this);RVInputMappings::Map(Mapping,A,Key,Name,Label);};
        Make(EquipAction,EKeys::Four,TEXT("EquipWeapon"),TEXT("Equip / holster handgun"));Make(FireAction,EKeys::LeftMouseButton,TEXT("Fire"),TEXT("Primary Attack"));
        Make(AimAction,EKeys::RightMouseButton,TEXT("Aim"),TEXT("Aim handgun"));Make(ReloadAction,EKeys::R,TEXT("Reload"),TEXT("Reload / stand up"));
        Make(UnloadAction,EKeys::U,TEXT("UnloadMagazine"),TEXT("Unload magazine to inventory"));
        Make(NextWeaponAction,EKeys::MouseScrollUp,TEXT("NextWeapon"),TEXT("Next weapon / equipment"));Make(PreviousWeaponAction,EKeys::MouseScrollDown,TEXT("PreviousWeapon"),TEXT("Previous weapon / equipment"));Make(EquipMeleeAction,EKeys::Five,TEXT("EquipMelee"),TEXT("Equip / holster melee tool"));
        // Shared defaults must still reach the accepted bed-wake/vehicle-orbit context.
        AimAction->bConsumeInput=false;ReloadAction->bConsumeInput=false;}
    if(auto* Local=PC->GetLocalPlayer())if(auto* S=Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
    {InputLocalPlayer=Local;RVInputMappings::Register(PC,Mapping);S->RemoveMappingContext(Mapping);S->AddMappingContext(Mapping,4);}
    Input->BindAction(EquipAction,ETriggerEvent::Started,this,&ThisClass::EquipInput);Input->BindAction(FireAction,ETriggerEvent::Started,this,&ThisClass::FireInput);
    Input->BindAction(AimAction,ETriggerEvent::Started,this,&ThisClass::AimStart);Input->BindAction(AimAction,ETriggerEvent::Completed,this,&ThisClass::AimStop);Input->BindAction(AimAction,ETriggerEvent::Canceled,this,&ThisClass::AimStop);
    Input->BindAction(ReloadAction,ETriggerEvent::Started,this,&ThisClass::ReloadInput);
    Input->BindAction(UnloadAction,ETriggerEvent::Started,this,&ThisClass::UnloadInput);
    Input->BindAction(NextWeaponAction,ETriggerEvent::Started,this,&ThisClass::NextWeaponInput);Input->BindAction(PreviousWeaponAction,ETriggerEvent::Started,this,&ThisClass::PreviousWeaponInput);Input->BindAction(EquipMeleeAction,ETriggerEvent::Started,this,&ThisClass::EquipMeleeInput);
}
void URVCombatComponent::RemoveInput()
{if(bLocalAimApplied){if(auto* Camera=GetOwner()->FindComponentByClass<UCameraComponent>())Camera->SetFieldOfView(UnaimedFOV);bLocalAimApplied=false;}
 if(auto* L=InputLocalPlayer.Get()){if(auto* S=L->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())S->RemoveMappingContext(Mapping);RVInputMappings::Unregister(L,Mapping);}InputLocalPlayer.Reset();}
void URVCombatComponent::EquipInput()
{FGuid Id;if(!EquippedWeapon.IsValid())for(const auto& W:Inventory()->GetItems())if(W.Definition && W.Definition->Combat.bFirearm){Id=W.Id;break;}
 GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Id]{ServerEquip(Id);}));}
void URVCombatComponent::EquipMeleeInput()
{FGuid Id;FRVItemInstance Current;if(!GetWeapon(Current) || !Current.Definition->Combat.bMelee)for(const auto& W:Inventory()->GetItems())if(W.Definition && W.Definition->Combat.bMelee){Id=W.Id;break;}
 GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Id]{ServerEquip(Id);}));}
void URVCombatComponent::MeleeInput()
{FGuid Id;int32 Revision=0;FRVItemInstance W;if(GetWeapon(W) && W.Definition->Combat.bMelee){Id=W.Id;Revision=W.CombatRevision;}
 const uint32 Request=++LocalMeleeRequest;GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Id,Revision,Request]{ServerMelee(Id,Revision,Request);}));}
void URVCombatComponent::ServerMelee_Implementation(FGuid Id,int32 Revision,uint32 Request)
{
    if(!GetOwner()->HasAuthority() || !CanUse() || Request==0 || Request<=LastMeleeRequest || ReloadEnds>0 || GetWorld()->GetTimeSeconds()<NextMeleeTime)return;
    FRVItemInstance W;const bool Armed=Id.IsValid();
    if(Armed && (Id!=EquippedWeapon || !GetWeapon(W) || !W.Definition->Combat.bMelee || W.CombatRevision!=Revision || W.Condition<=0))return;
    if(!Armed && GetWeapon(W) && W.Definition->Combat.bMelee)return;
    const auto* M=Armed?&W.Definition->Combat:nullptr;
    const float Range=M?M->MeleeRangeCm:ShoveRangeCm,Radius=M?M->MeleeSweepRadiusCm:8.f;
    const float Cooldown=M?M->MeleeCooldownSeconds:ShoveCooldownSeconds,Cost=M?M->MeleeFatigueCost:ShoveFatigueCost;
    const float Damage=M?M->Damage:ShoveDamage;
    if(!FMath::IsFinite(Range) || Range<=0 || Range>200 || !FMath::IsFinite(Radius) || Radius<0 || Radius>20 || !FMath::IsFinite(Cooldown) || Cooldown<.3f || !FMath::IsFinite(Damage) || Damage<0 || Damage>100)return;
    auto* Pawn=Cast<APawn>(GetOwner());auto* PS=Pawn?Pawn->GetPlayerState<ARVPlayerState>():nullptr;if(!PS || !PS->Needs->ApplyEffortAuthority(Cost))return;
    LastMeleeRequest=Request;NextMeleeTime=GetWorld()->GetTimeSeconds()+Cooldown;++MeleeSequence;
    int32 Variant=0;
    if(M && M->Presentation && M->Presentation->LightAttacks.Num()>1)
        Variant=(LastMeleeVariant+1)%M->Presentation->LightAttacks.Num();
    LastMeleeVariant=Variant;
    const float Delay=M && M->Presentation?FMath::Clamp(M->Presentation->LightAttackHitSeconds,.01f,.5f):.12f;
    GetWorld()->GetTimerManager().SetTimer(MeleeHitTimer,FTimerDelegate::CreateWeakLambda(this,[this,Id,Revision]{ResolveMeleeHit(Id,Revision);}),Delay,false);
    FVector Eye;FRotator Rotation;Pawn->GetActorEyesViewPoint(Eye,Rotation);
    UAISense_Hearing::ReportNoiseEvent(GetWorld(),Eye,.4f,Pawn,Armed?900:500,TEXT("Melee"));
    MulticastMelee(Armed,Variant);Feedback=Armed?TEXT("Melee swing"):TEXT("Defensive shove");GetOwner()->ForceNetUpdate();
}
void URVCombatComponent::ResolveMeleeHit(FGuid Id,int32 Revision)
{
    if(!GetOwner()->HasAuthority() || !CanUse())return;
    FRVItemInstance W;const bool Armed=Id.IsValid();
    if(Armed && (Id!=EquippedWeapon || !GetWeapon(W) || !W.Definition->Combat.bMelee || W.CombatRevision!=Revision))return;
    if(!Armed && EquippedWeapon.IsValid())return;
    auto* Pawn=Cast<APawn>(GetOwner());auto* PS=Pawn?Pawn->GetPlayerState<ARVPlayerState>():nullptr;if(!PS)return;
    const auto* M=Armed?&W.Definition->Combat:nullptr;
    const float Range=M?M->MeleeRangeCm:ShoveRangeCm,Radius=M?M->MeleeSweepRadiusCm:8.f,Damage=M?M->Damage:ShoveDamage;
    FVector Eye;FRotator Rotation;Pawn->GetActorEyesViewPoint(Eye,Rotation);const FVector End=Eye+Rotation.Vector()*Range;
    FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(RVMelee),true,Pawn);
    if(GetWorld()->SweepSingleByChannel(Hit,Eye,End,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(Radius),Params) && Hit.GetActor())
    {
        // A broad sweep may touch a target around a corner: require a clear impact ray too.
        FHitResult Obstruction;const bool Clear=!GetWorld()->LineTraceSingleByChannel(Obstruction,Eye,Hit.ImpactPoint,ECC_Visibility,Params) || Obstruction.GetActor()==Hit.GetActor();
        if(Clear)
        {bApplyingMelee=true;if(bFriendlyFire || !Cast<ARVSurvivorCharacter>(Hit.GetActor()))UGameplayStatics::ApplyPointDamage(Hit.GetActor(),Damage*(PS->Needs->State.Fatigue>=PS->Needs->Tuning.FatigueCritical?.65f:1.f),Rotation.Vector(),Hit,Pawn->GetController(),Pawn,nullptr);bApplyingMelee=false;
         if(auto* Infected=Cast<ARVInfected>(Hit.GetActor()))Infected->StaggerAuthority(Armed?.35f:.7f);}
    }
}
void URVCombatComponent::MulticastMelee_Implementation(bool Armed,int32 Variant)
{
    auto* C=Cast<ACharacter>(GetOwner());if(!C)return;
    FRVItemInstance W;UAnimMontage* Montage=ShoveMontage;
    if(Armed && GetWeapon(W))
    {const auto* P=W.Definition->Combat.Presentation.Get();Montage=P && P->LightAttacks.IsValidIndex(Variant)?P->LightAttacks[Variant].Get():W.Definition->Combat.MeleeMontage.Get();}
    if(Montage)C->PlayAnimMontage(Montage);
}
void URVCombatComponent::FireInput()
{FRVItemInstance W;if(!GetWeapon(W) || !W.Definition->Combat.bFirearm){MeleeInput();return;}const uint32 Request=++LocalRequest;GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,W,Request]{ServerFire(W.Id,W.CombatRevision,Request);}));}
void URVCombatComponent::ReloadInput()
{FRVItemInstance W;if(!CanUse() || !GetWeapon(W))return;FGuid Best;int32 Rounds=-1;for(const auto& M:Inventory()->GetItems())if(M.Definition && M.Definition->Combat.bMagazine
 && !M.LoadedInWeapon.IsValid() && M.Definition->Combat.Caliber==W.Definition->Combat.Caliber && M.MagazineRounds>Rounds){Best=M.Id;Rounds=M.MagazineRounds;}
 GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Best,W]{ServerReload(Best,W.CombatRevision);}));}
void URVCombatComponent::AimStart(){GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this]{ServerAim(true);}));}
void URVCombatComponent::UnloadInput(){GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this]{ServerUnload();}));}
void URVCombatComponent::AimStop(){GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this]{ServerAim(false);}));}
void URVCombatComponent::EndPlay(const EEndPlayReason::Type Reason)
{RemoveInput();CancelReload();GetWorld()->GetTimerManager().ClearTimer(MeleeHitTimer);if(GetOwner()->HasAuthority() && Inventory())Inventory()->ReleaseMagazineAuthority(EquippedWeapon);Super::EndPlay(Reason);}
bool URVCombatComponent::DebugRequestFire(FGuid Weapon,int32 Revision,int32 Request)
{
#if !UE_BUILD_SHIPPING && !UE_BUILD_TEST
    const auto* P=Cast<APawn>(GetOwner());if(!P || !P->IsLocallyControlled() || !GetWorld()->IsGameWorld() || Request<1)return false;
    GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Weapon,Revision,Request]{ServerFire(Weapon,Revision,uint32(Request));}));return true;
#else
    return false;
#endif
}
bool URVCombatComponent::DebugRequestReload(FGuid Magazine,int32 Revision)
{
#if !UE_BUILD_SHIPPING && !UE_BUILD_TEST
    const auto* P=Cast<APawn>(GetOwner());if(!P || !P->IsLocallyControlled() || !GetWorld()->IsGameWorld())return false;
    GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Magazine,Revision]{ServerReload(Magazine,Revision);}));return true;
#else
    return false;
#endif
}




bool URVCombatComponent::GetOwnerGripTargets(FTransform& Primary,FVector& Support) const
{
    const auto* C=Cast<ACharacter>(GetOwner());FRVItemInstance W;
    if(!C || !CanUse() || ReloadEnds>0 || !GetWeapon(W))return false;
    const auto& A=W.Definition->Combat;const auto* Family=A.Presentation.Get();
    if(!Family || Family->Family!=ERVWeaponFamily::Handgun)return false;
    const auto* Visual=C->FindComponentByClass<URVCharacterPresentationComponent>();
    const auto* Anchor=Visual?Visual->GetEquipmentAnchor(A.HandAnchor):nullptr;if(!Anchor)return false;
    // Left effector is in the primary bone's space, evaluated after the right arm.
    const FTransform Grip=A.GripOffset*(C->IsLocallyControlled()?A.FirstPersonOffset:A.ThirdPersonOffset)*(C->IsLocallyControlled()?Family->FirstPersonOffset:Family->ThirdPersonOffset)*Anchor->GetRelativeTransform();
    Support=Grip.TransformPosition(A.SupportHandTarget.GetLocation());
    if(!C->IsLocallyControlled())return true;
    const auto* Camera=C->FindComponentByClass<UCameraComponent>();if(!Camera)return false;
    const float Pitch=FMath::Clamp(FRotator::NormalizeAxis(C->GetBaseAimRotation().Pitch),-70.f,70.f)*Family->UpperBodyPitchScale;
    const FQuat PitchRotation=FRotator(Pitch,0,0).Quaternion();
    FTransform Ready=Family->ReadyHand;
    Ready.SetLocation(Family->AimPivot+PitchRotation.RotateVector(Ready.GetLocation()-Family->AimPivot));
    Ready.SetRotation(PitchRotation*Ready.GetRotation());
    Ready=Ready*C->GetActorTransform();
    if(A.bSightADS && AimBlend>0)
    {
        const FTransform Sight(Camera->GetComponentQuat(),Camera->GetComponentLocation()+Camera->GetForwardVector()*A.SightEyeReliefCm);
        const FTransform ADS=Grip.Inverse()*A.SightTransform.Inverse()*Sight;
        Primary.Blend(Ready,ADS,AimBlend);
    }
    else Primary=Ready;
    return true;
}
TArray<FGuid> URVCombatComponent::GetQuickAccessItems() const
{
    TArray<FRVItemInstance> Items;
    if(const auto* I=Inventory())for(const auto& W:I->GetItems())
        if(W.Definition && W.Definition->bEquippable && W.Condition>0 && (W.Definition->Combat.bFirearm || W.Definition->Combat.bMelee || W.Definition->Combat.bQuickAccess))Items.Add(W);
    Items.Sort([](const auto& A,const auto& B){const int32 X=A.Definition->Combat.QuickAccessOrder,Y=B.Definition->Combat.QuickAccessOrder;return X==Y?A.Id.ToString()<B.Id.ToString():X<Y;});
    TArray<FGuid> Result;Result.Add(FGuid());for(const auto& W:Items)Result.Add(W.Id);return Result;
}
void URVCombatComponent::ServerCycleEquipment_Implementation(int32 Direction)
{
    if(!GetOwner()->HasAuthority() || !CanUse() || (Direction!=1 && Direction!=-1))return;
    const auto Items=GetQuickAccessItems();if(Items.Num()<2)return;
    int32 Index=Items.IndexOfByKey(EquippedWeapon);if(Index==INDEX_NONE)Index=0;
    ServerEquip(Items[(Index+Direction+Items.Num())%Items.Num()]);
}
void URVCombatComponent::NextWeaponInput()
{const auto* P=Cast<APawn>(GetOwner());const auto* PC=P?Cast<APlayerController>(P->GetController()):nullptr;if(PC && !PC->bShowMouseCursor)ServerCycleEquipment(1);}
void URVCombatComponent::PreviousWeaponInput()
{const auto* P=Cast<APawn>(GetOwner());const auto* PC=P?Cast<APlayerController>(P->GetController()):nullptr;if(PC && !PC->bShowMouseCursor)ServerCycleEquipment(-1);}
