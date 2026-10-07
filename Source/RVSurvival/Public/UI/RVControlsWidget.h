#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "RVControlsWidget.generated.h"
UCLASS()
class RVSURVIVAL_API URVControlRowWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    FName MappingName;
    FText Label;
    FKey CurrentKey;
protected:
    virtual TSharedRef<SWidget> RebuildWidget() override;
    UFUNCTION() void Selected(FInputChord Chord);
};
UCLASS()
class RVSURVIVAL_API URVControlsWidget : public UUserWidget
{
    GENERATED_BODY()
protected:
    virtual TSharedRef<SWidget> RebuildWidget() override;
    virtual FReply NativeOnKeyDown(const FGeometry& Geometry,const FKeyEvent& Event) override;
    UFUNCTION() void Close();
};
