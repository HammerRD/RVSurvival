#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Inventory/RVInventoryComponent.h"
#include "RVCombatComponent.generated.h"
class UStaticMeshComponent;
class UInputAction;
class UEnhancedInputComponent;
class UInputMappingContext;
class ULocalPlayer;

/** Owned intents only. Server derives trace, validates state and consumes an inventory round. */
UCLASS(ClassGroup=(RV),meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVCombatComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVCombatComponent();
    virtual void TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Function) override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    void BindInput(UEnhancedInputComponent* Input);
    void RemoveInput();
    UPROPERTY(EditAnywhere,BlueprintReadOnly) bool bEnabled=false;
    UPROPERTY(Replicated,BlueprintReadOnly) FGuid EquippedWeapon;
    UPROPERTY(Replicated,BlueprintReadOnly) bool bAiming=false;
    UPROPERTY(Replicated,BlueprintReadOnly) double ReloadEnds=0;
    UPROPERTY(Replicated,BlueprintReadOnly) int32 ShotSequence=0;
    UPROPERTY(Replicated,BlueprintReadOnly) int32 MeleeSequence=0;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) TObjectPtr<class UAnimMontage> ShoveMontage;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) float ShoveRangeCm=110;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) float ShoveCooldownSeconds=1.2f;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) float ShoveDamage=3;
    UPROPERTY(EditDefaultsOnly,BlueprintReadOnly) float ShoveFatigueCost=.15f;
    bool IsApplyingMeleeDamage() const {return bApplyingMelee;}
    UPROPERTY(Replicated,BlueprintReadOnly) FString Feedback;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) bool bFriendlyFire=true;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float AimFOVScale=.8f;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) float AimSensitivityScale=.7f;
    float GetLookScale() const {return bEnabled && bAiming?AimSensitivityScale:1.f;}
    UFUNCTION(BlueprintPure) int32 GetLoadedRounds() const;
    UFUNCTION(BlueprintPure) bool GetWeapon(FRVItemInstance& Item) const;
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly)) bool DebugRequestFire(FGuid Weapon,int32 Revision,int32 RequestSequence);
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly)) bool DebugRequestReload(FGuid Magazine,int32 Revision);
    UFUNCTION(Server,Reliable) void ServerEquip(FGuid Id);
    UFUNCTION(Server,Reliable) void ServerAim(bool Value);
    UFUNCTION(Server,Reliable) void ServerFire(FGuid Weapon,int32 Revision,uint32 RequestSequence);
    UFUNCTION(Server,Reliable) void ServerReload(FGuid Magazine,int32 WeaponRevision);
    UFUNCTION(Server,Reliable) void ServerUnload();
    UFUNCTION(Server,Reliable) void ServerMelee(FGuid Weapon,int32 Revision,uint32 RequestSequence);
    UFUNCTION(NetMulticast,Unreliable) void MulticastMelee(bool Armed);
    UFUNCTION(NetMulticast,Unreliable) void MulticastShot(FVector_NetQuantize Start,FVector_NetQuantize End);
private:
    URVInventoryComponent* Inventory() const;
    bool CanUse() const;
    void EquipInput();
    void EquipMeleeInput();
    void MeleeInput();
    void FireInput();
    void ReloadInput();
    void UnloadInput();
    void AimStart();
    void AimStop();
    void FinishReload();
    void CancelReload();
    void UpdateVisual();
    FTimerHandle ReloadTimer;
    FGuid ReloadMagazine;
    int32 ReloadRevision=0;
    double NextShotTime=0;
    double NextMeleeTime=0;
    uint32 LastMeleeRequest=0;
    uint32 LocalMeleeRequest=0;
    bool bApplyingMelee=false;
    float AimBlend=0;
    uint32 LastRequest=0;
    uint32 LocalRequest=0;
    float UnaimedFOV=0;
    bool bLocalAimApplied=false;
    bool bHitQueriesConfigured=false;
    double PresentedReloadEnd=0;
    UPROPERTY(Transient) TObjectPtr<UStaticMeshComponent> WeaponVisual;
    UPROPERTY(Transient) TObjectPtr<URVItemDefinition> VisualDefinition;
    UPROPERTY(Transient) TArray<TObjectPtr<class URVBodyRegionHitComponent>> HitQueries;
    UPROPERTY(Transient) TObjectPtr<UInputMappingContext> Mapping;
    UPROPERTY(Transient) TObjectPtr<UInputAction> EquipAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> FireAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> AimAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> ReloadAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> UnloadAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> MeleeAction;
    UPROPERTY(Transient) TObjectPtr<UInputAction> EquipMeleeAction;
    TWeakObjectPtr<ULocalPlayer> InputLocalPlayer;
};
