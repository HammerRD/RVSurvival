#include "UI/RVMechanicalWidget.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/VerticalBox.h"
#include "Components/TextBlock.h"
#include "Components/ProgressBar.h"
#include "Player/RVPlayerController.h"
#include "Player/RVPassengerReferenceFrameComponent.h"
#include "Vehicles/RVMechanicalMotorhome.h"
#include "Mechanical/RVCoolingComponent.h"
#include "Mechanical/RVServicePoint.h"
#include "GameFramework/GameStateBase.h"
#include "Vehicles/RVInteractiveDoor.h"
void URVMechanicalWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    auto* Border=WidgetTree->ConstructWidget<UBorder>();Border->SetPadding(FMargin(14));Border->SetBrushColor(FLinearColor(.025f,.045f,.055f,.95f));WidgetTree->RootWidget=Border;
    auto* Root=WidgetTree->ConstructWidget<UVerticalBox>();Border->SetContent(Root);
    Title=WidgetTree->ConstructWidget<UTextBlock>();Temperature=WidgetTree->ConstructWidget<UTextBlock>();Warnings=WidgetTree->ConstructWidget<UTextBlock>();Service=WidgetTree->ConstructWidget<UTextBlock>();Gauge=WidgetTree->ConstructWidget<UProgressBar>();
    for(auto* Text:{Title.Get(),Temperature.Get(),Warnings.Get(),Service.Get()})
    {auto Font=Text->GetFont();Font.Size=16;Text->SetFont(Font);Text->SetColorAndOpacity(FSlateColor(FLinearColor(.85f,.9f,.88f)));Text->SetAutoWrapText(true);Text->SetWrapTextAt(340);}
    Title->SetText(FText::FromString(TEXT("MOTORHOME | ENGINE / COOLING")));
    Root->AddChildToVerticalBox(Title);Root->AddChildToVerticalBox(Temperature);Root->AddChildToVerticalBox(Gauge);Root->AddChildToVerticalBox(Warnings);Root->AddChildToVerticalBox(Service);
    SetVisibility(ESlateVisibility::HitTestInvisible);
}
void URVMechanicalWidget::NativeTick(const FGeometry& G,float DT)
{
    Super::NativeTick(G,DT);const auto* PC=Cast<ARVPlayerController>(GetOwningPlayer());if(!PC)return;
    auto* RV=PC->MechanicalPoint?PC->MechanicalPoint->Vehicle.Get():Cast<ARVMechanicalMotorhome>(PC->SeatedVehicle.Get());
    if(!RV && PC->GetPawn())
        if(auto* Frame=PC->GetPawn()->FindComponentByClass<URVPassengerReferenceFrameComponent>())RV=Cast<ARVMechanicalMotorhome>(Frame->ReferenceFrame.Get());
    SetVisibility(RV?ESlateVisibility::HitTestInvisible:ESlateVisibility::Collapsed);if(!RV)return;
    const auto* C=RV->CoolingSystem.Get();const auto& S=C->Cooling;
    const TCHAR* Name=S.Status==ERVThermalStatus::Normal?TEXT("Normal"):S.Status==ERVThermalStatus::Warm?TEXT("Warm"):S.Status==ERVThermalStatus::Hot?TEXT("Hot"):S.Status==ERVThermalStatus::Overheating?TEXT("Overheating"):TEXT("CRITICAL");
    Temperature->SetText(FText::FromString(FString::Printf(TEXT("Temperature %.0f C | %s"),S.TemperatureC,Name)));
    Gauge->SetPercent(float(FMath::Clamp((S.TemperatureC-40)/100.,0.,1.)));Gauge->SetFillColorAndOpacity(S.Status>=ERVThermalStatus::Hot?FLinearColor(.95f,.3f,.12f):FLinearColor(.3f,.75f,.6f));
    FString Warning;
    if(S.CoolantLitres<C->Tuning.CoolantCapacityLitres*C->Tuning.LowCoolantFraction)Warning+=TEXT("LOW COOLANT  ");
    if(S.LeakLitresPerSecond>0)Warning+=TEXT("COOLING LEAK  ");
    if(C->Engine.bShutdown)Warning+=TEXT("ENGINE SHUTDOWN - SERVICE REQUIRED");else if(C->Engine.OutputScale<.99f)Warning+=TEXT("LIMITED ENGINE OUTPUT");
    if(RV->EngineHood && RV->EngineHood->bOpen)Warning+=TEXT(" HOOD OPEN - ENGINE INTERLOCK");
    Warnings->SetText(FText::FromString(Warning.IsEmpty()?TEXT("No cooling warnings"):Warning));
    FString Detail;
    if(PC->MechanicalPoint)
    {
        Detail=FString::Printf(TEXT("Coolant: %s | Radiator: %s | Engine: %s\nP hood | B patch | N radiator replacement | M engine service\nI inventory, select coolant then F refill | Escape close/cancel\n%s"),S.CoolantLitres<C->Tuning.CoolantCapacityLitres*C->Tuning.LowCoolantFraction?TEXT("low"):TEXT("present"),S.bTemporaryPatch?TEXT("temporarily patched"):S.RadiatorCondition<C->Tuning.MinorDamageThreshold?TEXT("damaged"):TEXT("serviceable"),C->Engine.Condition<.5f?TEXT("damaged"):TEXT("serviceable"),*PC->MechanicalFeedback);
        if(PC->MechanicalPoint->RepairPlayer)
        {
            const auto* GS=GetWorld()->GetGameState();const double Now=GS?GS->GetServerWorldTimeSeconds():GetWorld()->GetTimeSeconds();
            const double Progress=PC->MechanicalPoint->RepairDuration>0?FMath::Clamp((Now-PC->MechanicalPoint->RepairStart)/PC->MechanicalPoint->RepairDuration,0.,1.):0;
            Detail+=FString::Printf(TEXT("\nRepair in progress: %s | %.0f%%"),*PC->MechanicalPoint->ActiveRepair.ToString(),Progress*100);
        }
    }
    Service->SetText(FText::FromString(Detail));
}
