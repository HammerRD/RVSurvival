#include "UI/RVSurvivalWidget.h"
#include "Blueprint/WidgetTree.h"
#include "Components/VerticalBox.h"
#include "Components/TextBlock.h"
#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
#include "Medical/RVHealthComponent.h"
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
    MedicalStatus=WidgetTree->ConstructWidget<UTextBlock>();MedicalStatus->SetFont(Font);
    MedicalStatus->SetAutoWrapText(true);MedicalStatus->SetWrapTextAt(650);
    MedicalStatus->SetColorAndOpacity(FSlateColor(FLinearColor(1,.65f,.4f)));Root->AddChildToVerticalBox(MedicalStatus);
    SetVisibility(ESlateVisibility::HitTestInvisible);
}
void URVSurvivalWidget::NativeTick(const FGeometry& Geometry,float Delta)
{
    Super::NativeTick(Geometry,Delta);
    const auto* PC=GetOwningPlayer(); const auto* PS=PC?PC->GetPlayerState<ARVPlayerState>():nullptr;
    auto* Needs=PS?PS->Needs.Get():nullptr;
    if(PS && PS->Health && MedicalStatus)
    {
        FString Warning;
        const auto* H=PS->Health.Get();
        if(H->LifeState==ERVMedicalLifeState::Downed)Warning=TEXT("DOWNED — teammate treatment required");
        else if(H->LifeState==ERVMedicalLifeState::Terminal)Warning=TEXT("Terminal condition (prototype)");
        else
        {
            float Worst=0;for(const auto& I:H->Injuries)if(I.BleedingPerMinute>0)Worst=FMath::Max(Worst,I.Severity);
            if(Worst>0)Warning=Worst>=3?TEXT("SEVERE BLEEDING — urgent treatment"):TEXT("Bleeding — treatment needed");
            else if(H->GetMovementScale()<1)Warning=TEXT("Leg injury — mobility restricted");
            else if(H->GetPain()>15)Warning=TEXT("Pain — inspect injuries");
        }
        if(!Warning.IsEmpty())Warning+=TEXT(" | ")+RVInputMappings::KeyLabel(GetOwningPlayer(),TEXT("Medical"),TEXT("F9"))+TEXT(" Medical");
        MedicalStatus->SetText(FText::FromString(Warning));
    }
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
