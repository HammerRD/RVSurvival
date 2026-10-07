#include "UI/RVSurvivalWidget.h"
#include "Blueprint/WidgetTree.h"
#include "Components/VerticalBox.h"
#include "Components/TextBlock.h"
#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
#include "GameFramework/PlayerController.h"
#include "Player/RVInputMappings.h"
void URVSurvivalWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    auto* Root=WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(),TEXT("SurvivalReadout"));
    WidgetTree->RootWidget=Root;
    Values=WidgetTree->ConstructWidget<UTextBlock>(); Status=WidgetTree->ConstructWidget<UTextBlock>();
    FSlateFontInfo Font=Values->GetFont(); Font.Size=20; Values->SetFont(Font); Status->SetFont(Font);
    Values->SetColorAndOpacity(FSlateColor(FLinearColor::White)); Status->SetColorAndOpacity(FSlateColor(FLinearColor(1.f,.8f,.3f)));
    Root->AddChildToVerticalBox(Values);Root->AddChildToVerticalBox(Status);
    SetVisibility(ESlateVisibility::HitTestInvisible);
}
void URVSurvivalWidget::NativeTick(const FGeometry& Geometry,float Delta)
{
    Super::NativeTick(Geometry,Delta);
    const auto* PC=GetOwningPlayer(); const auto* PS=PC?PC->GetPlayerState<ARVPlayerState>():nullptr;
    auto* Needs=PS?PS->Needs.Get():nullptr;
    if(BoundNeeds.Get()!=Needs)
    {
        if(BoundNeeds.IsValid()) BoundNeeds->OnNeedsChanged.RemoveDynamic(this,&URVSurvivalWidget::Refresh);
        BoundNeeds=Needs;
        if(Needs) Needs->OnNeedsChanged.AddUniqueDynamic(this,&URVSurvivalWidget::Refresh);
        Refresh();
    }
}
void URVSurvivalWidget::NativeDestruct()
{
    if(BoundNeeds.IsValid()) BoundNeeds->OnNeedsChanged.RemoveDynamic(this,&URVSurvivalWidget::Refresh);
    BoundNeeds.Reset(); Super::NativeDestruct();
}
void URVSurvivalWidget::Refresh()
{
    const auto* Needs=BoundNeeds.Get();
    if(!Needs || !Values || !Status) return;
    Values->SetText(FText::FromString(FString::Printf(TEXT("Nutrition %.0f | Hydration %.0f | Fatigue %.0f"),Needs->State.Nutrition,Needs->State.Hydration,Needs->State.Fatigue)));
    // Replicated needs remain input-independent; translate prototype hints locally.
    FString Hints=Needs->GetWarnings()+TEXT("  ")+Needs->Feedback;
    Hints.ReplaceInline(TEXT("R / E:"),*(RVInputMappings::KeyLabel(GetOwningPlayer(),TEXT("Stand"),TEXT("R"))+TEXT(" / ")+RVInputMappings::KeyLabel(GetOwningPlayer(),TEXT("Interact"),TEXT("E"))+TEXT(":")),ESearchCase::CaseSensitive);
    Hints.ReplaceInline(TEXT("Z:"),*(RVInputMappings::KeyLabel(GetOwningPlayer(),TEXT("Sleep"),TEXT("Z"))+TEXT(":")),ESearchCase::CaseSensitive);
    Hints.ReplaceInline(TEXT("R: retry"),*(RVInputMappings::KeyLabel(GetOwningPlayer(),TEXT("Stand"),TEXT("R"))+TEXT(": retry")),ESearchCase::CaseSensitive);
    Status->SetText(FText::FromString(Hints));
}
