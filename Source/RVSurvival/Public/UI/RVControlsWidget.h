#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Core/RVDifficultyProfile.h"
#include "RVControlsWidget.generated.h"
UCLASS()
class RVSURVIVAL_API URVControlRowWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    FName MappingName;
    FText Label;
    FKey CurrentKey;
    FKey PendingKey;
    bool bUpdatingSelector=false;
    UPROPERTY(Transient) TObjectPtr<class UTextBlock> Warning;
    UPROPERTY(Transient) TObjectPtr<class UInputKeySelector> Selector;
    UPROPERTY(Transient) TObjectPtr<class UComboBoxString> AxisChoices;
protected:
    virtual TSharedRef<SWidget> RebuildWidget() override;
    UFUNCTION() void Selected(FInputChord Chord);
    UFUNCTION() void AxisSelected(FString Option,ESelectInfo::Type SelectionType);
    UFUNCTION() class UWidget* AxisEntry(FString Option);
};
UCLASS()
class RVSURVIVAL_API URVDifficultyRowWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    FRVDifficultyRule Rule;
    int32 Revision=0;
    bool bPersonal=false;
protected:
    virtual TSharedRef<SWidget> RebuildWidget() override;
    UFUNCTION() void Changed(float Value);
    UFUNCTION() void Commit();
    float PendingValue=1;
    UPROPERTY(Transient) TObjectPtr<class UTextBlock> ValueText;
};
UCLASS()
class RVSURVIVAL_API URVPresetWidget : public UUserWidget
{
    GENERATED_BODY()
public:
    FName Preset;
protected:
    virtual TSharedRef<SWidget> RebuildWidget() override;
    UFUNCTION() void Select();
};
UCLASS()
class RVSURVIVAL_API URVControlsWidget : public UUserWidget
{
    GENERATED_BODY()
protected:
    virtual TSharedRef<SWidget> RebuildWidget() override;
    virtual FReply NativeOnKeyDown(const FGeometry& Geometry,const FKeyEvent& Event) override;
    virtual void NativeTick(const FGeometry& Geometry,float Delta) override;
    UFUNCTION() void Close();
    UFUNCTION() void ResetBindings();
    UFUNCTION() void InvertChanged(bool Enabled);
    void Populate();
    UPROPERTY(Transient) TObjectPtr<class UScrollBox> Rows;
    int32 ShownRevision=-1;
};
