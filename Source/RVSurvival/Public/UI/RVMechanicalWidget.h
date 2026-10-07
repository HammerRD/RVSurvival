#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "RVMechanicalWidget.generated.h"
/** Read-only presentation; control intent remains on the owned controller. */
UCLASS()
class RVSURVIVAL_API URVMechanicalWidget : public UUserWidget
{
    GENERATED_BODY()
protected:
    virtual void NativeOnInitialized()override;
    virtual void NativeTick(const FGeometry& Geometry,float DT)override;
private:
    UPROPERTY(Transient) TObjectPtr<class UTextBlock> Title;
    UPROPERTY(Transient) TObjectPtr<class UTextBlock> Temperature;
    UPROPERTY(Transient) TObjectPtr<class UTextBlock> Warnings;
    UPROPERTY(Transient) TObjectPtr<class UTextBlock> Service;
    UPROPERTY(Transient) TObjectPtr<class UProgressBar> Gauge;
};
