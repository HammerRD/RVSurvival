#include "UI/RVMedicalWidget.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/VerticalBox.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "Player/RVPlayerState.h"
#include "Player/RVPlayerController.h"
#include "Player/RVSurvivorCharacter.h"
#include "Medical/RVHealthComponent.h"
#include "Inventory/RVInventoryComponent.h"
#include "Survival/RVNeedsComponent.h"
#include "GameFramework/GameStateBase.h"
#include "EngineUtils.h"
#include "Vehicles/RVVehicleBase.h"
#include "Vehicles/RVVehicleSeatComponent.h"
void URVMedicalWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    auto* Border=WidgetTree->ConstructWidget<UBorder>(); Border->SetPadding(FMargin(18));
    Border->SetBrushColor(FLinearColor(.025f,.045f,.055f,.97f)); WidgetTree->RootWidget=Border;
    auto* Root=WidgetTree->ConstructWidget<UVerticalBox>(); Border->SetContent(Root);
    auto Text=[&](const FString& Value){auto* T=WidgetTree->ConstructWidget<UTextBlock>();auto Font=T->GetFont();Font.Size=16;T->SetFont(Font);T->SetText(FText::FromString(Value));T->SetAutoWrapText(true);T->SetWrapTextAt(440);Root->AddChildToVerticalBox(T);return T;};
    Text(TEXT("MEDICAL | ASSESS / STABILIZE / RECOVER")); Summary=Text(TEXT("Assessing")); Selection=Text(TEXT("Select injury and supply")); Feedback=Text(TEXT(""));
    auto Button=[&](const TCHAR* Label){auto* B=WidgetTree->ConstructWidget<UButton>();auto* T=WidgetTree->ConstructWidget<UTextBlock>();T->SetText(FText::FromString(Label));B->AddChild(T);Root->AddChildToVerticalBox(B);return B;};
    Button(TEXT("Inspect self"))->OnClicked.AddDynamic(this,&ThisClass::Self);
    Button(TEXT("Inspect nearby teammate"))->OnClicked.AddDynamic(this,&ThisClass::Nearby);
    Button(TEXT("Next injury"))->OnClicked.AddDynamic(this,&ThisClass::NextInjury);
    Button(TEXT("Next medical supply"))->OnClicked.AddDynamic(this,&ThisClass::NextSupply);
    Button(TEXT("Begin treatment / revive"))->OnClicked.AddDynamic(this,&ThisClass::Treat);
    Button(TEXT("Cancel treatment (retain supply)"))->OnClicked.AddDynamic(this,&ThisClass::Cancel);
    Button(TEXT("Close — resume walking"))->OnClicked.AddDynamic(this,&ThisClass::Close);
    Self();
}
void URVMedicalWidget::Self() { Patient=GetOwningPlayer()->GetPlayerState<ARVPlayerState>(); InjuryIndex=0; }
void URVMedicalWidget::Nearby()
{
    auto* PC=GetOwningPlayer(); if(!PC->GetPawn()) return;
    float Closest=200; Patient.Reset();
    for(TActorIterator<ARVSurvivorCharacter> It(GetWorld());It;++It)
    {
        auto* PS=It->GetPlayerState<ARVPlayerState>();
        // Native vehicle possession clears the unpossessed survivor's PlayerState.
        // Only the replicated driver occupant may use the vehicle's PlayerState.
        if(!PS && It->SeatedVehicle)
            for(const auto* Seat:It->SeatedVehicle->GetSeats())
                if(Seat && Seat->bDriverSeat && Seat->Occupant==*It)
                { PS=It->SeatedVehicle->GetPlayerState<ARVPlayerState>(); break; }
        if(PS && PS!=PC->GetPlayerState<ARVPlayerState>())
        { const float D=FVector::Dist(It->GetActorLocation(),PC->GetPawn()->GetActorLocation());if(D<Closest){Closest=D;Patient=PS;} }
    }
    InjuryIndex=0;
}
void URVMedicalWidget::NextInjury() { ++InjuryIndex; }
void URVMedicalWidget::NextSupply() { ++SupplyIndex; }
void URVMedicalWidget::Cancel() { if(auto* PS=GetOwningPlayer()->GetPlayerState<ARVPlayerState>())PS->Health->RequestCancelTreatment(); }
void URVMedicalWidget::Close() { if(auto* PC=Cast<ARVPlayerController>(GetOwningPlayer()))PC->ToggleMedical(); }
void URVMedicalWidget::Treat()
{
    auto* PS=GetOwningPlayer()->GetPlayerState<ARVPlayerState>(); auto* Target=Patient.Get();
    auto* C=PS?PS->Needs->ResolveSurvivor():nullptr;auto* Inventory=C?C->FindComponentByClass<URVInventoryComponent>():nullptr;
    if(!PS || !Target || !Inventory) return;
    auto Items=Inventory->GetItems();Items.RemoveAll([](const auto& I){return !I.Definition || !I.Definition->Medical.bMedicalSupply;});
    if(Items.IsEmpty()) return;
    const auto& Item=Items[SupplyIndex%Items.Num()];
    if(Target->Health->Injuries.IsEmpty())
    {if(Item.Definition->Medical.Treatment==ERVTreatmentKind::Revive)PS->Health->RequestTreatment(Target,FGuid::NewGuid(),Item.Id,0);return;}
    const auto& Injury=Target->Health->Injuries[InjuryIndex%Target->Health->Injuries.Num()];
    PS->Health->RequestTreatment(Target,Injury.Id,Item.Id,Injury.Revision);
}
void URVMedicalWidget::NativeTick(const FGeometry& G,float Delta)
{
    Super::NativeTick(G,Delta);
    auto* PS=GetOwningPlayer()->GetPlayerState<ARVPlayerState>(); auto* Target=Patient.Get();
    if(!PS || !Target){Summary->SetText(FText::FromString(TEXT("No nearby patient — choose self or approach teammate")));return;}
    auto* H=Target->Health.Get();FString Status=H->LifeState==ERVMedicalLifeState::Active?TEXT("Conscious"):H->LifeState==ERVMedicalLifeState::Downed?TEXT("DOWNED — urgent stabilization"):TEXT("Terminal (prototype)");
    Status+=FString::Printf(TEXT(" | Pain: %s\n"),H->GetPain()>50?TEXT("severe"):H->GetPain()>15?TEXT("noticeable"):TEXT("low"));
    static const TCHAR* Regions[]={TEXT("Head"),TEXT("Torso"),TEXT("Left arm"),TEXT("Right arm"),TEXT("Left leg"),TEXT("Right leg")};
    static const TCHAR* Types[]={TEXT("Wound"),TEXT("Fracture"),TEXT("Burn"),TEXT("Concussion")};
    if(!H->Injuries.IsEmpty())
    {const auto& I=H->Injuries[InjuryIndex%H->Injuries.Num()];Status+=FString::Printf(TEXT("%s — %s | %s\n%s | %s | %s"),Regions[uint8(I.Region)],Types[uint8(I.Kind)],I.Severity>=3?TEXT("severe"):I.Severity>=2?TEXT("moderate"):TEXT("minor"),I.BleedingPerMinute>0?TEXT("ACTIVE BLEEDING"):TEXT("No active bleeding"),I.Healing>=1?TEXT("Recovered"):I.bStabilized?TEXT("Stabilized; recovery needed"):I.Healing>0?TEXT("Recovering"):TEXT("Untreated"),I.InfectionRisk>=.3f?TEXT("Contamination risk"):TEXT("Low contamination risk"));}
    else Status+=TEXT("No recorded injuries");Summary->SetText(FText::FromString(Status));
    auto* C=PS->Needs->ResolveSurvivor();auto* Inventory=C?C->FindComponentByClass<URVInventoryComponent>():nullptr;
    auto Items=Inventory?Inventory->GetItems():TArray<FRVItemInstance>();Items.RemoveAll([](const auto& I){return !I.Definition || !I.Definition->Medical.bMedicalSupply;});
    Selection->SetText(FText::FromString(Items.IsEmpty()?TEXT("Transfer medical supplies to your inventory first"):FString::Printf(TEXT("Supply: %s × %d"),*Items[SupplyIndex%Items.Num()].Definition->DisplayName.ToString(),Items[SupplyIndex%Items.Num()].Quantity)));
    FString Detail=PS->Health->Feedback;
    if(PS->Health->ActiveTreatment.IsValid())Detail+=FString::Printf(TEXT("\nTreatment: %.1f s remaining"),FMath::Max(0.,PS->Health->TreatmentEndTime-GetWorld()->GetGameState()->GetServerWorldTimeSeconds()));
    Feedback->SetText(FText::FromString(Detail));
}

