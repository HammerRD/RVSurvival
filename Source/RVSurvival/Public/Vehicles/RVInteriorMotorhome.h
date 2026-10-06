#pragma once
#include "CoreMinimal.h"
#include "Vehicles/RVMotorhome.h"
#include "GameplayTagContainer.h"
#include "RVInteriorMotorhome.generated.h"
USTRUCT(BlueprintType)
struct FRVVisualPart
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName Name;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TObjectPtr<class UStaticMesh> Mesh;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FTransform Transform;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) TArray<TObjectPtr<class UMaterialInterface>> Materials;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bDisallowNanite = false;
};
USTRUCT(BlueprintType)
struct FRVInteriorCollision
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName Name;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FVector Center = FVector::ZeroVector;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FVector Extent = FVector(10);
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bPassengerFloor = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bVisiblePrototype = false;
};
USTRUCT(BlueprintType)
struct FRVExteriorCompartmentDefinition
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName DoorPartName;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FText DisplayName;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FVector Position = FVector::ZeroVector;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FVector QueryExtent = FVector(30,3,20);
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float MaxWeightKg = 100;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float MaxVolumeLitres = 120;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FGameplayTagContainer AllowedTags;
};
USTRUCT(BlueprintType)
struct FRVStationDefinition
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FName Name;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) FVector Position = FVector::ZeroVector;
};
/** Art-independent mobile-base layout. Static art never supplies character/Chaos collision. */
UCLASS(Blueprintable)
class RVSURVIVAL_API ARVInteriorMotorhome : public ARVMotorhome
{
    GENERATED_BODY()
public:
    ARVInteriorMotorhome(const FObjectInitializer& Initializer);
    virtual void OnConstruction(const FTransform& Transform) override;
    virtual void BeginPlay() override;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<class UBoxComponent> InteriorFloor;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="RV|Presentation") TArray<FRVVisualPart> VisualParts;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="RV|Interior") TArray<FRVInteriorCollision> InteriorCollision;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="RV|Interior") TArray<FRVStationDefinition> Stations;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="RV|Storage") TArray<FRVExteriorCompartmentDefinition> ExteriorCompartments;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="RV|Entry") bool bEnableStandingDoor = false;
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="RV|Entry") FVector StandingEntryLocation = FVector(130,0,180);
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="RV|Entry") FVector OutsideDoorLocation = FVector(122,148,140);
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="RV|Entry") FVector InsideDoorLocation = FVector(122,75,150);
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="RV|Entry") bool bInteriorSeatAccess = false;
    bool TryStandingDoor(class ARVSurvivorCharacter* Character, bool bEnter);
    UFUNCTION(BlueprintPure, Category="RV|Presentation") class UStaticMeshComponent* FindVisualPart(FName PartName) const;
    UFUNCTION(BlueprintCallable, Category="RV|Configuration") void ConfigureProjectChassisCollision(FVector Center, FVector Extent);
    UFUNCTION(BlueprintCallable, Category="RV|Configuration") void RefreshConfiguration();
    UFUNCTION(BlueprintCallable, Category="RV|Configuration") static TArray<FVector> InspectArtSurfaces(class UStaticMesh* ArtMesh);
private:
    UPROPERTY(Transient) TArray<TObjectPtr<class USceneComponent>> GeneratedParts;
};

