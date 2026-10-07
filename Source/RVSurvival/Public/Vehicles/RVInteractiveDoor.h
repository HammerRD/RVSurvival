#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Interaction/RVInteractable.h"
#include "RVInteractiveDoor.generated.h"
/** Project-side hinged art and query collision; reusable independently of vehicle physics. */
UCLASS()
class RVSURVIVAL_API ARVInteractiveDoor : public AActor, public IRVInteractable
{
    GENERATED_BODY()
public:
    ARVInteractiveDoor();
    virtual void BeginPlay() override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual bool CanInteract_Implementation(APawn* Pawn) const override;
    virtual FText GetInteractionText_Implementation(APawn* Pawn) const override;
    virtual float GetInteractionDuration_Implementation(APawn*) const override { return .5f; }
    virtual void CompleteInteraction_Implementation(APawn* Pawn) override;
    UPROPERTY(ReplicatedUsing=OnRep_Door,BlueprintReadOnly) bool bOpen=false;
    UPROPERTY(EditAnywhere,ReplicatedUsing=OnRep_Door,BlueprintReadOnly) float OpenAngle=-90;
    // House doors retain yaw. A separate hood can reuse the same replicated hinge.
    UPROPERTY(EditAnywhere,ReplicatedUsing=OnRep_Door,BlueprintReadOnly) bool bPitchHinge=false;
    UPROPERTY(EditAnywhere,ReplicatedUsing=OnRep_Door,BlueprintReadOnly) TObjectPtr<class UStaticMesh> DoorMesh;
    UPROPERTY(EditAnywhere,ReplicatedUsing=OnRep_Door,BlueprintReadOnly) TObjectPtr<class UStaticMesh> GlassMesh;
    UPROPERTY(EditAnywhere,ReplicatedUsing=OnRep_Door,BlueprintReadOnly) TArray<TObjectPtr<class UMaterialInterface>> DoorMaterials;
    UPROPERTY(EditAnywhere,ReplicatedUsing=OnRep_Door,BlueprintReadOnly) TArray<TObjectPtr<class UMaterialInterface>> GlassMaterials;
    UPROPERTY(EditAnywhere,ReplicatedUsing=OnRep_Door,BlueprintReadOnly) FVector GlassOffset=FVector(0,0,62.87);
    UPROPERTY(EditAnywhere,ReplicatedUsing=OnRep_Door,BlueprintReadOnly) FVector CollisionCenter=FVector(-34,-2,0);
    UPROPERTY(EditAnywhere,ReplicatedUsing=OnRep_Door,BlueprintReadOnly) FVector CollisionExtent=FVector(34,3,112);
    UPROPERTY(EditAnywhere,Replicated,BlueprintReadOnly) FText DoorLabel;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<class UBoxComponent> DoorCollision;
    UFUNCTION(BlueprintPure) bool IsSwingClear(bool ToOpen) const;
private:
    UFUNCTION() void OnRep_Door();
    UPROPERTY() TObjectPtr<class USceneComponent> Hinge;
    UPROPERTY() TObjectPtr<class UStaticMeshComponent> Visual;
    UPROPERTY() TObjectPtr<class UStaticMeshComponent> Glass;
};
