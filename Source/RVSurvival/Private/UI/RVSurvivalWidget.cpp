#include "UI/RVSurvivalWidget.h"
#include "Blueprint/WidgetTree.h"
#include "Components/VerticalBox.h"
#include "Components/TextBlock.h"
#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
#include "GameFramework/PlayerController.h"
void URVSurvivalWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    auto* Root=WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(),TEXT("SurvivalReadout"));
    WidgetTree->RootWidget=Root;
    Values=WidgetTree->ConstructWidget<UTextBlock>(); Status=WidgetTree->ConstructWidget<UTextBlock>();
    FSlateFontInfo Font=Values->GetFont(); Font.Size=12; Values->SetFont(Font); Status->SetFont(Font);
    Values->SetColorAndOpacity(FSlateColor(FLinearColor::White)); Status->SetColorAndOpacity(FSlateColor(FLinearColor(1,.8,.3)));
    Root->AddChildToVerticalBox(Values);Root->AddChildToVerticalBox(Status);
    SetVisibility(ESlateVisibility::HitTestInvisible);
}
void URVSurvivalWidget::NativeTick(const FGeometry& Geometry,float Delta)
{
    Super::NativeTick(Geometry,Delta); RefreshElapsed+=Delta;
    if(RefreshElapsed<.25f) return; RefreshElapsed=0;
    const auto* PC=GetOwningPlayer(); const auto* PS=PC?PC->GetPlayerState<ARVPlayerState>():nullptr;
    if(!PS || !PS->Needs || !Values || !Status) return;
    const auto* Needs=PS->Needs.Get();
    Values->SetText(FText::FromString(FString::Printf(TEXT("Nutrition %.0f | Hydration %.0f | Fatigue %.0f"),Needs->State.Nutrition,Needs->State.Hydration,Needs->State.Fatigue)));
    Status->SetText(FText::FromString(Needs->GetWarnings()+TEXT("  ")+Needs->Feedback));
}
