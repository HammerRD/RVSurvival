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
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<URVCoolingComponent> CoolingSystem;
    virtual float GetMechanicalOutputScale() const override;
    virtual bool CanOperateEngine() const override;
};
