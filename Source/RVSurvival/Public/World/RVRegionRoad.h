#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RVRegionRoad.generated.h"
class USplineComponent;
class UStaticMesh;
class UMaterialInterface;

/** Authored native spline-mesh road segment. Static, nonreplicated world content. */
UCLASS()
class RVSURVIVAL_API ARVRegionRoad : public AActor
{
    GENERATED_BODY()
public:
    ARVRegionRoad();
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<USplineComponent> Route;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) TObjectPtr<UStaticMesh> RoadMesh;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) TObjectPtr<UMaterialInterface> Asphalt;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) TObjectPtr<UMaterialInterface> CenterPaint;
    UPROPERTY(EditAnywhere,BlueprintReadOnly,meta=(ClampMin="400",ClampMax="2400")) float WidthCm=900;
    virtual void OnConstruction(const FTransform& Transform) override;
    UFUNCTION(BlueprintCallable,CallInEditor) void RebuildRoad();
};
