#include "UI/RVControlsWidget.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/VerticalBox.h"
#include "Components/HorizontalBox.h"
#include "Components/TextBlock.h"
#include "Components/InputKeySelector.h"
#include "Components/Button.h"
#include "Components/ScrollBox.h"
#include "Components/VerticalBoxSlot.h"
#include "Player/RVPlayerController.h"
#include "Engine/LocalPlayer.h"
#include "EnhancedInputSubsystems.h"
#include "UserSettings/EnhancedInputUserSettings.h"
TSharedRef<SWidget> URVControlRowWidget::RebuildWidget()
{
    auto* Row=WidgetTree->ConstructWidget<UHorizontalBox>();WidgetTree->RootWidget=Row;
    auto* Text=WidgetTree->ConstructWidget<UTextBlock>();Text->SetText(Label);Row->AddChildToHorizontalBox(Text);
    auto* Key=WidgetTree->ConstructWidget<UInputKeySelector>();Key->SetAllowGamepadKeys(false);Key->SetAllowModifierKeys(false);
    Key->SetSelectedKey(FInputChord(CurrentKey));Key->OnKeySelected.AddDynamic(this,&ThisClass::Selected);Row->AddChildToHorizontalBox(Key);
    return Super::RebuildWidget();
}
void URVControlRowWidget::Selected(FInputChord Chord)
{
    auto* PC=GetOwningPlayer();if(!PC || !Chord.Key.IsValid() || Chord.Key==EKeys::Escape)return;
    if(auto* Subsystem=PC->GetLocalPlayer()->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
        if(auto* Settings=Subsystem->GetUserSettings())
        {
            FMapPlayerKeyArgs Args;Args.MappingName=MappingName;Args.NewKey=Chord.Key;Args.Slot=EPlayerMappableKeySlot::First;
            FGameplayTagContainer Failures;Settings->MapPlayerKey(Args,Failures);
            if(Failures.IsEmpty()){Settings->ApplySettings();Settings->AsyncSaveSettings();}
        }
}
TSharedRef<SWidget> URVControlsWidget::RebuildWidget()
{
    SetIsFocusable(true);
    auto* Border=WidgetTree->ConstructWidget<UBorder>();Border->SetBrushColor(FLinearColor(.025f,.025f,.025f,.97f));Border->SetPadding(FMargin(24));WidgetTree->RootWidget=Border;
    auto* Box=WidgetTree->ConstructWidget<UVerticalBox>();Border->SetContent(Box);
    auto* Title=WidgetTree->ConstructWidget<UTextBlock>();Title->SetText(FText::FromString(TEXT("Controls | select a key to change it | Escape closes")));Title->SetAutoWrapText(true);Box->AddChildToVerticalBox(Title);
    auto* Scroll=WidgetTree->ConstructWidget<UScrollBox>();Box->AddChildToVerticalBox(Scroll)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
    if(auto* PC=GetOwningPlayer())if(auto* Subsystem=PC->GetLocalPlayer()->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
        if(auto* Settings=Subsystem->GetUserSettings())if(auto* Profile=Settings->GetActiveKeyProfile())
        {
            TArray<FName> Names;Profile->GetPlayerMappingRows().GetKeys(Names);Names.Sort(FNameLexicalLess());
            for(FName Name:Names)for(const auto& Mapping:Profile->GetPlayerMappingRows()[Name].Mappings)
                if(Mapping.GetSlot()==EPlayerMappableKeySlot::First)
                {auto* Row=CreateWidget<URVControlRowWidget>(PC);Row->MappingName=Name;Row->Label=Mapping.GetDisplayName();Row->CurrentKey=Mapping.GetCurrentKey();Scroll->AddChild(Row);break;}
        }
    auto* Button=WidgetTree->ConstructWidget<UButton>();auto* Text=WidgetTree->ConstructWidget<UTextBlock>();Text->SetText(FText::FromString(TEXT("Return to game")));Button->SetContent(Text);Button->OnClicked.AddDynamic(this,&ThisClass::Close);Box->AddChildToVerticalBox(Button);
    return Super::RebuildWidget();
}
void URVControlsWidget::Close(){if(auto* PC=Cast<ARVPlayerController>(GetOwningPlayer()))PC->ToggleControls();}
FReply URVControlsWidget::NativeOnKeyDown(const FGeometry& Geometry,const FKeyEvent& Event)
{if(Event.GetKey()==EKeys::Escape){Close();return FReply::Handled();}return Super::NativeOnKeyDown(Geometry,Event);}
