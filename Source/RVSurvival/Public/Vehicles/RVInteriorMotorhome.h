#pragma once
#include "CoreMinimal.h"
#include "Vehicles/RVMotorhome.h"
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
    UFUNCTION(BlueprintCallable, Category="RV|Configuration") void ConfigureProjectChassisCollision(FVector Center, FVector Extent);
    UFUNCTION(BlueprintCallable, Category="RV|Configuration") void RefreshConfiguration();
    UFUNCTION(BlueprintCallable, Category="RV|Configuration") static TArray<FVector> InspectArtSurfaces(class UStaticMesh* ArtMesh);
private:
    UPROPERTY(Transient) TArray<TObjectPtr<class USceneComponent>> GeneratedParts;
};

