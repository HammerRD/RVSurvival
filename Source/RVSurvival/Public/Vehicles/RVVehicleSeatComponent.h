#pragma once
#include "CoreMinimal.h"
#include "Components/SceneComponent.h"
#include "RVVehicleSeatComponent.generated.h"
class ARVSurvivorCharacter;
class ARVPlayerController;
/** Stable named default subobjects; authority alone changes occupancy. */
UCLASS(ClassGroup=(RV), meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVVehicleSeatComponent : public USceneComponent
{
    GENERATED_BODY()
public:
    URVVehicleSeatComponent();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Seat") bool bDriverSeat = false;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Seat") FText SeatLabel;
    // Only this cushion/back is exempt from the seated upper-body clearance query.
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Seat") FName SurfaceCollisionName;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Seat") bool bEnabled=true;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Seat") bool bInteriorOnly=false;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Seat") bool bUsePrototypeSittingPose=false;
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Seat") FVector StandingAisleLocation=FVector(130,0,180);
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Seat") FVector EntryOffset = FVector(0, 180, 60);
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Seat") FVector ExitOffset = FVector(0, 280, 0);
    UPROPERTY(Replicated, BlueprintReadOnly, Category="Seat") TObjectPtr<ARVSurvivorCharacter> Occupant;
    // Controllers are intentionally not exposed to other clients.
    TWeakObjectPtr<ARVPlayerController> OccupantController;
};
