#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "RVMedicalWidget.generated.h"
UCLASS()
class RVSURVIVAL_API URVMedicalWidget : public UUserWidget
{
    GENERATED_BODY()
protected:
    virtual void NativeOnInitialized() override;
    virtual void NativeTick(const FGeometry& Geometry,float Delta) override;
private:
    UFUNCTION() void Self();
    UFUNCTION() void Nearby();
    UFUNCTION() void NextInjury();
    UFUNCTION() void NextSupply();
    UFUNCTION() void Treat();
    UFUNCTION() void Cancel();
    UFUNCTION() void Close();
    UPROPERTY(Transient) TObjectPtr<class UTextBlock> Summary;
    UPROPERTY(Transient) TObjectPtr<class UTextBlock> Selection;
    UPROPERTY(Transient) TObjectPtr<class UTextBlock> Feedback;
    TWeakObjectPtr<class ARVPlayerState> Patient;
    int32 InjuryIndex=0;
    int32 SupplyIndex=0;
};
