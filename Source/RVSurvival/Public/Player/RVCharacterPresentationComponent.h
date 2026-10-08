#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Medical/RVMedicalProfile.h"
#include "RVCharacterPresentationComponent.generated.h"
class URVCharacterVisualProfile;
class USceneComponent;
UENUM(BlueprintType)
enum class ERVCharacterVisualState : uint8 { Locomotion, Driver, Passenger, Bed, Downed, Ladder, Treatment };
/** Reads existing replicated states. Changes presentation only, never the capsule/base. */
UCLASS(ClassGroup=(RV),meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVCharacterPresentationComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVCharacterPresentationComponent();
    virtual void BeginPlay() override;
    virtual void TickComponent(float Delta,ELevelTick Type,FActorComponentTickFunction* Function) override;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<URVCharacterVisualProfile> Profile;
    UPROPERTY(BlueprintReadOnly) ERVCharacterVisualState VisualState=ERVCharacterVisualState::Locomotion;
    UFUNCTION(BlueprintPure) bool HasConfiguredVisuals() const;
    UFUNCTION(BlueprintPure) bool ResolveBodyRegion(FName Bone,ERVBodyRegion& Region) const;
    UFUNCTION(BlueprintPure) FTransform GetBodyRegionTransform(ERVBodyRegion Region) const;
    UFUNCTION(BlueprintPure) USceneComponent* GetEquipmentAnchor(FName Id) const;
    void RefreshVisualState();
private:
    bool bInitialized=false;
    bool bHeadHidden=false;
    int32 Placement=-1;
    UPROPERTY(Transient) TMap<FName,TObjectPtr<USceneComponent>> Anchors;
};
