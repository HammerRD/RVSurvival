#pragma once
#include "CoreMinimal.h"
#include "Vehicles/RVSystemsMotorhome.h"
#include "RVMechanicalMotorhome.generated.h"
class URVCoolingComponent;
UCLASS(Blueprintable)
class RVSURVIVAL_API ARVMechanicalMotorhome : public ARVSystemsMotorhome
{
    GENERATED_BODY()
public:
    ARVMechanicalMotorhome(const FObjectInitializer& Init);
    virtual void BeginPlay() override;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) FVector EngineServiceLocation=FVector(416,0,120);
    UPROPERTY(Replicated,BlueprintReadOnly) TObjectPtr<class ARVServicePoint> EngineService;
    UPROPERTY(EditAnywhere,BlueprintReadOnly) FName HoodPartName=TEXT("Art_RV_Chassis_Hood");
    UPROPERTY(EditAnywhere,BlueprintReadOnly) FVector HoodCollisionCenter=FVector(70,0,12);
    UPROPERTY(EditAnywhere,BlueprintReadOnly) FVector HoodCollisionExtent=FVector(73,90,6);
    UPROPERTY(Replicated,BlueprintReadOnly) TObjectPtr<class ARVInteractiveDoor> EngineHood;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<URVCoolingComponent> CoolingSystem;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<class URVRecoveryComponent> Recovery;
    virtual float GetMechanicalOutputScale() const override;
    virtual bool CanOperateEngine() const override;
};
