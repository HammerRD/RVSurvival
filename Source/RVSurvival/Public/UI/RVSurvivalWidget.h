#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "RVSurvivalWidget.generated.h"
/** Presentation only. Reads the owning PlayerState; never owns survival values. */
UCLASS()
class RVSURVIVAL_API URVSurvivalWidget : public UUserWidget
{
    GENERATED_BODY()
protected:
    virtual void NativeOnInitialized() override;
    virtual void NativeTick(const FGeometry& Geometry,float Delta) override;
private:
    UPROPERTY(Transient) TObjectPtr<class UTextBlock> Values;
    UPROPERTY(Transient) TObjectPtr<class UTextBlock> Status;
    float RefreshElapsed=0;
};
