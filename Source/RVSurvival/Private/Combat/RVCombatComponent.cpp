#include "Combat/RVCombatComponent.h"
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
#include "NativeGameplayTags.h"
#include "Animation/AnimMontage.h"
#include "Engine/StaticMeshActor.h"
#include "Components/PointLightComponent.h"
UE_DEFINE_GAMEPLAY_TAG_STATIC(TAG_RV9mm,"Item.Ammo.9mm");

URVCombatComponent::URVCombatComponent(){SetIsReplicatedByDefault(true);PrimaryComponentTick.bCanEverTick=true;}
URVInventoryComponent* URVCombatComponent::Inventory() const{return GetOwner()->FindComponentByClass<URVInventoryComponent>();}
bool URVCombatComponent::GetWeapon(FRVItemInstance& Item) const
{if(const auto* I=Inventory())for(const auto& W:I->GetItems())if(W.Id==EquippedWeapon){Item=W;return W.Definition && W.Definition->Combat.bFirearm;}return false;}
int32 URVCombatComponent::GetLoadedRounds() const
{if(const auto* I=Inventory())for(const auto& M:I->GetItems())if(EquippedWeapon.IsValid() && M.LoadedInWeapon==EquippedWeapon)return M.MagazineRounds;return 0;}
bool URVCombatComponent::CanUse() const
{
    const auto* C=Cast<ARVSurvivorCharacter>(GetOwner());if(!bEnabled || !C || !C->GetController() || C->SeatedVehicle)return false;
    const auto* PS=C->GetPlayerState<ARVPlayerState>();if(!PS || !PS->Health->CanAct() || PS->Health->ActiveTreatment.IsValid() || PS->Needs->State.RestMode!=ERVRestMode::Awake)return false;
    const auto* L=C->FindComponentByClass<URVLadderClimbComponent>();return !L || !L->Ladder;
}
void URVCombatComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(URVCombatComponent,EquippedWeapon);DOREPLIFETIME(URVCombatComponent,bAiming);DOREPLIFETIME(URVCombatComponent,ReloadEnds);DOREPLIFETIME(URVCombatComponent,ShotSequence);DOREPLIFETIME_CONDITION(URVCombatComponent,Feedback,COND_OwnerOnly);}
void URVCombatComponent::ServerEquip_Implementation(FGuid Id)
{
    if(!GetOwner()->HasAuthority())return;
    if(!CanUse()){Feedback=TEXT("Cannot equip in this state");return;}
    if(Id.IsValid())
    {bool Owned=false;for(const auto& W:Inventory()->GetItems())if(W.Id==Id && W.Definition && W.Definition->Combat.bFirearm && W.Definition->bEquippable)Owned=true;
     if(!Owned){Feedback=TEXT("Weapon not owned");return;}}
    CancelReload(); // Holstering preserves the magazine physically loaded in this owned gun.
    EquippedWeapon=Id;bAiming=false;Feedback.Empty();GetOwner()->ForceNetUpdate();
}
void URVCombatComponent::ServerAim_Implementation(bool Value){if(!GetOwner()->HasAuthority())return;bAiming=Value && CanUse() && EquippedWeapon.IsValid();GetOwner()->ForceNetUpdate();}
void URVCombatComponent::ServerFire_Implementation(FGuid Weapon,int32 Revision,uint32 Request)
{
    if(!GetOwner()->HasAuthority())return;
    if(Request==0 || Request<=LastRequest)return;
    FRVItemInstance W;
    if(!CanUse() || ReloadEnds>0 || Weapon!=EquippedWeapon || !GetWeapon(W)){Feedback=TEXT("Cannot fire in this state");return;}
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
    FRVItemInstance W;if(!CanUse() || ReloadEnds>0 || !GetWeapon(W) || W.CombatRevision!=Revision){Feedback=TEXT("Cannot reload stale weapon");return;}
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
        const FVector Muzzle=WeaponVisual?WeaponVisual->GetComponentTransform().TransformPosition(FVector(12,0,0)):FVector(Start);
        Effect(Muzzle,.035f,.08f,true);Effect(End,.025f,.5f,false);
    }
    // Bounded prototype effect. Cosmetic loss never repeats an authoritative shot.
    DrawDebugLine(GetWorld(),Start,End,FColor::Yellow,false,.08f,0,.7f);DrawDebugPoint(GetWorld(),End,5,FColor::Orange,false,.3f);
    if(auto* P=Cast<APawn>(GetOwner());P && P->IsLocallyControlled())if(auto* PC=Cast<APlayerController>(P->GetController());PC && GetWeapon(W))PC->AddPitchInput(-W.Definition->Combat.RecoilPitch);
}
void URVCombatComponent::UpdateVisual()
{
    auto* C=Cast<ACharacter>(GetOwner());if(!C)return;FRVItemInstance W;
    auto* D=GetWeapon(W)?W.Definition.Get():nullptr;
    if(!WeaponVisual){WeaponVisual=NewObject<UStaticMeshComponent>(GetOwner(),TEXT("EquippedFirearmVisual"));WeaponVisual->SetCollisionEnabled(ECollisionEnabled::NoCollision);WeaponVisual->RegisterComponent();}
    if(D!=VisualDefinition){VisualDefinition=D;WeaponVisual->SetStaticMesh(D?D->WorldMesh.LoadSynchronous():nullptr);
        if(D)if(auto* P=C->FindComponentByClass<URVCharacterPresentationComponent>())if(auto* A=P->GetEquipmentAnchor(D->Combat.HandAnchor))
        {WeaponVisual->AttachToComponent(A,FAttachmentTransformRules::SnapToTargetNotIncludingScale);WeaponVisual->SetRelativeTransform(D->Combat.GripOffset);}}
    const auto* PS=C->GetPlayerState<ARVPlayerState>();
    const auto* Survivor=Cast<ARVSurvivorCharacter>(C);
    const auto* Climb=C->FindComponentByClass<URVLadderClimbComponent>();
    WeaponVisual->SetVisibility(D && bEnabled && PS && PS->Health->CanAct() && !PS->Health->ActiveTreatment.IsValid()
        && PS->Needs->State.RestMode==ERVRestMode::Awake && (!Climb || !Climb->Ladder) && (!Survivor || !Survivor->SeatedVehicle));
    if(ReloadEnds!=PresentedReloadEnd)
    {PresentedReloadEnd=ReloadEnds;if(D && D->Combat.ReloadMontage)
      {if(ReloadEnds>0){const auto* GS=GetWorld()->GetGameState();const float Remaining=ReloadEnds-(GS?GS->GetServerWorldTimeSeconds():GetWorld()->GetTimeSeconds());
        if(Remaining>.05f)C->PlayAnimMontage(D->Combat.ReloadMontage,D->Combat.ReloadMontage->GetPlayLength()/Remaining);}
       else C->StopAnimMontage(D->Combat.ReloadMontage);}}
    if(C->IsLocallyControlled())if(auto* Camera=C->FindComponentByClass<UCameraComponent>())
    {const bool Aim=bAiming && CanUse();if(Aim && !bLocalAimApplied){UnaimedFOV=Camera->FieldOfView;Camera->SetFieldOfView(UnaimedFOV*AimFOVScale);}
     else if(!Aim && bLocalAimApplied)Camera->SetFieldOfView(UnaimedFOV);bLocalAimApplied=Aim;}
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
        Make(EquipAction,EKeys::Four,TEXT("EquipWeapon"),TEXT("Equip / holster handgun"));Make(FireAction,EKeys::LeftMouseButton,TEXT("Fire"),TEXT("Fire handgun"));
        Make(AimAction,EKeys::RightMouseButton,TEXT("Aim"),TEXT("Aim handgun"));Make(ReloadAction,EKeys::R,TEXT("Reload"),TEXT("Reload / stand up"));
        Make(UnloadAction,EKeys::U,TEXT("UnloadMagazine"),TEXT("Unload magazine to inventory"));
        // Shared defaults must still reach the accepted bed-wake/vehicle-orbit context.
        AimAction->bConsumeInput=false;ReloadAction->bConsumeInput=false;}
    if(auto* Local=PC->GetLocalPlayer())if(auto* S=Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
    {InputLocalPlayer=Local;RVInputMappings::Register(PC,Mapping);S->RemoveMappingContext(Mapping);S->AddMappingContext(Mapping,4);}
    Input->BindAction(EquipAction,ETriggerEvent::Started,this,&ThisClass::EquipInput);Input->BindAction(FireAction,ETriggerEvent::Started,this,&ThisClass::FireInput);
    Input->BindAction(AimAction,ETriggerEvent::Started,this,&ThisClass::AimStart);Input->BindAction(AimAction,ETriggerEvent::Completed,this,&ThisClass::AimStop);Input->BindAction(AimAction,ETriggerEvent::Canceled,this,&ThisClass::AimStop);
    Input->BindAction(ReloadAction,ETriggerEvent::Started,this,&ThisClass::ReloadInput);
    Input->BindAction(UnloadAction,ETriggerEvent::Started,this,&ThisClass::UnloadInput);
}
void URVCombatComponent::RemoveInput()
{if(bLocalAimApplied){if(auto* Camera=GetOwner()->FindComponentByClass<UCameraComponent>())Camera->SetFieldOfView(UnaimedFOV);bLocalAimApplied=false;}
 if(auto* L=InputLocalPlayer.Get()){if(auto* S=L->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())S->RemoveMappingContext(Mapping);RVInputMappings::Unregister(L,Mapping);}InputLocalPlayer.Reset();}
void URVCombatComponent::EquipInput()
{FGuid Id;if(!EquippedWeapon.IsValid())for(const auto& W:Inventory()->GetItems())if(W.Definition && W.Definition->Combat.bFirearm){Id=W.Id;break;}
 GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Id]{ServerEquip(Id);}));}
void URVCombatComponent::FireInput()
{FRVItemInstance W;if(!GetWeapon(W))return;const uint32 Request=++LocalRequest;GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,W,Request]{ServerFire(W.Id,W.CombatRevision,Request);}));}
void URVCombatComponent::ReloadInput()
{FRVItemInstance W;if(!CanUse() || !GetWeapon(W))return;FGuid Best;int32 Rounds=-1;for(const auto& M:Inventory()->GetItems())if(M.Definition && M.Definition->Combat.bMagazine
 && !M.LoadedInWeapon.IsValid() && M.Definition->Combat.Caliber==W.Definition->Combat.Caliber && M.MagazineRounds>Rounds){Best=M.Id;Rounds=M.MagazineRounds;}
 GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Best,W]{ServerReload(Best,W.CombatRevision);}));}
void URVCombatComponent::AimStart(){GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this]{ServerAim(true);}));}
void URVCombatComponent::UnloadInput(){GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this]{ServerUnload();}));}
void URVCombatComponent::AimStop(){GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this]{ServerAim(false);}));}
void URVCombatComponent::EndPlay(const EEndPlayReason::Type Reason)
{RemoveInput();CancelReload();if(GetOwner()->HasAuthority() && Inventory())Inventory()->ReleaseMagazineAuthority(EquippedWeapon);Super::EndPlay(Reason);}
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
