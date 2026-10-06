#include "UI/RVPrototypeHUD.h"
#include "Vehicles/RVSystemsMotorhome.h"
#include "Vehicles/RVResourcePoint.h"
#include "Resources/RVElectricalComponent.h"
#include "Player/RVSurvivorCharacter.h"
#include "Interaction/RVInteractionComponent.h"
#include "Engine/Canvas.h"
#include "GameFramework/PlayerController.h"
#include "Player/RVPlayerController.h"
#include "Vehicles/RVVehicleBase.h"
#include "Inventory/RVInventoryComponent.h"
#include "InputCoreTypes.h"
#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
#include "UI/RVSurvivalWidget.h"
void ARVPrototypeHUD::EndPlay(const EEndPlayReason::Type Reason)
{
    if(SurvivalWidget) { SurvivalWidget->RemoveFromParent(); SurvivalWidget=nullptr; }
    Super::EndPlay(Reason);
}
void ARVPrototypeHUD::DrawHUD()
{
    Super::DrawHUD();
    if (!Canvas || !PlayerOwner) return;
    auto* PS=PlayerOwner->GetPlayerState<ARVPlayerState>();
    auto* Needs=PS?PS->Needs.Get():nullptr;
    if(Needs)
    {
        if(!SurvivalWidget && PlayerOwner->IsLocalController())
        {
            SurvivalWidget=CreateWidget<URVSurvivalWidget>(PlayerOwner,URVSurvivalWidget::StaticClass());
            SurvivalWidget->AddToPlayerScreen();
            // UE's position setter resets anchors: apply bottom anchoring afterwards.
            SurvivalWidget->SetPositionInViewport(FVector2D(20,-15),false);
            SurvivalWidget->SetAnchorsInViewport(FAnchors(0,1)); SurvivalWidget->SetAlignmentInViewport(FVector2D(0,1));
        }
        if(PlayerOwner->WasInputKeyJustPressed(EKeys::R)) Needs->RequestRestMode(ERVRestMode::Awake);
        if(PlayerOwner->WasInputKeyJustPressed(EKeys::Z)) Needs->RequestRestMode(Needs->State.RestMode==ERVRestMode::Sleeping?ERVRestMode::Resting:ERVRestMode::Sleeping);
    }
    if(auto* PC=Cast<ARVPlayerController>(PlayerOwner))
    {
        auto* V=PC->ResourcePoint?PC->ResourcePoint->Vehicle.Get():Cast<ARVSystemsMotorhome>(PC->SeatedVehicle.Get());
        if(V)
        {
            auto* Bus=V->Electrical.Get();
            const float X=FMath::Max(20.f,Canvas->ClipX-370.f);
            DrawRect(FLinearColor(0,0,0,.75),X,110,350,245);
            DrawText(FString::Printf(TEXT("RV monitor | Fuel %.2f / %.0f L"),V->PropulsionFuel->Litres,V->PropulsionFuel->CapacityLitres),FLinearColor::White,X+10,120,nullptr,.85);
            DrawText(FString::Printf(TEXT("House %.0f%% (%.1f Wh) | Chassis %.0f%%"),V->HouseBattery->GetStateOfCharge()*100,V->HouseBattery->EnergyWh,V->ChassisBattery->GetStateOfCharge()*100),FLinearColor::White,X+10,145,nullptr,.8);
            DrawText(FString::Printf(TEXT("Generator %s | solar %.0f%% | idle %s"),Bus->bGeneratorRunning?TEXT("ON"):TEXT("off"),Bus->SolarInput*100,Bus->bEngineIdleRequested?TEXT("ON"):TEXT("off")),FLinearColor::White,X+10,170,nullptr,.8);
            DrawText(FString::Printf(TEXT("Load %.0f/%.0f W | battery %+.0f W"),Bus->Flow.SuppliedWatts,Bus->Flow.RequestedWatts,Bus->Flow.HouseBatteryWatts),FLinearColor::White,X+10,195,nullptr,.8);
            int32 Line=0;
            for(const auto& Load:Bus->Loads) DrawText(FString::Printf(TEXT("%s: %s / %s"),*Load.DisplayName.ToString(),Load.bEnabled?TEXT("on"):TEXT("off"),Load.bPowered?TEXT("powered"):TEXT("no power")),FLinearColor::White,X+10,220+(Line++)*18,nullptr,.75);
            DrawText(PC->ResourceFeedback,FLinearColor::Yellow,X+10,310,nullptr,.75);
            if(PC->ResourcePoint && !PC->ResourcePoint->bFuelFill)
            {
                DrawText(TEXT("H lights | J generator | K fridge | L tools | O idle"),FLinearColor::White,X+10,333,nullptr,.7);
                auto Switch=[&](FName Name,FKey Key)
                { if(PlayerOwner->WasInputKeyJustPressed(Key)) { const auto* Load=Bus->Loads.FindByPredicate([&](const auto& Item){return Item.Id==Name;}); if(Load) PC->RequestResourceControl(Name,!Load->bEnabled,Bus->ControlRevision); } };
                Switch(TEXT("InteriorLights"),EKeys::H); Switch(TEXT("Refrigerator"),EKeys::K); Switch(TEXT("PoweredStation"),EKeys::L);
                if(PlayerOwner->WasInputKeyJustPressed(EKeys::J)) PC->RequestResourceControl(TEXT("Generator"),!Bus->bGeneratorRunning,Bus->ControlRevision);
                if(PlayerOwner->WasInputKeyJustPressed(EKeys::O)) PC->RequestResourceControl(TEXT("EngineIdle"),!Bus->bEngineIdleRequested,Bus->ControlRevision);
            }
            if(PC->ResourcePoint && PlayerOwner->WasInputKeyJustPressed(EKeys::Escape)) PC->RequestCloseResource();
        }
    }
    DrawText(TEXT("+"), FLinearColor::White, Canvas->ClipX * 0.5f, Canvas->ClipY * 0.5f);
    if (const auto* PC = Cast<ARVPlayerController>(PlayerOwner); PC && PC->SeatedVehicle)
    {
        const bool Driver = PlayerOwner->GetPawn() == PC->SeatedVehicle;
        DrawText(Driver ? TEXT("PROTOTYPE RV | W: accelerate  S: brake/reverse  A/D: steer  Space: handbrake  E: exit when stopped")
            : TEXT("RV passenger | E: exit when stopped"), FLinearColor::White, 20, 35);
        DrawText(TEXT("Stopped: 1 driver | 2 passenger | V next free seat"), FLinearColor::White, 20, 60);
        DrawText(PC->SeatFeedback, FLinearColor::Yellow, 20, 85);
        return;
    }
    if (const auto* Pawn = Cast<ARVSurvivorCharacter>(PlayerOwner->GetPawn()))
    {
        DrawText(Pawn->GetInteraction()->GetPrompt().ToString(), FLinearColor::White,
            Canvas->ClipX * 0.5f - 150.f, Canvas->ClipY * 0.5f + 35.f);
        auto* Inventory=Pawn->FindComponentByClass<URVInventoryComponent>();
        if(!Inventory) return;
        if(Inventory->OpenContainer != LastContainer.Get())
        { LastContainer=Inventory->OpenContainer; if(LastContainer.IsValid()) bInventoryVisible=true; SelectedRow=0; }
        if(PlayerOwner->WasInputKeyJustPressed(EKeys::I))
        { bInventoryVisible=!bInventoryVisible; if(!bInventoryVisible) Inventory->RequestCloseContainer(); }
        if(!bInventoryVisible) { DrawText(TEXT("I: inventory"),FLinearColor::White,20,65); return; }
        if(PlayerOwner->WasInputKeyJustPressed(EKeys::Tab)) { bSelectContainer=!bSelectContainer; SelectedRow=0; }
        if(PlayerOwner->WasInputKeyJustPressed(EKeys::Down)) ++SelectedRow;
        if(PlayerOwner->WasInputKeyJustPressed(EKeys::Up)) --SelectedRow;
        auto* Selected=bSelectContainer?Inventory->OpenContainer.Get():Inventory;
        const TArray<FRVItemInstance> Items=Selected?Selected->GetItems():TArray<FRVItemInstance>();
        SelectedRow=FMath::Clamp(SelectedRow,0,FMath::Max(0,Items.Num()-1));
        if(Items.IsValidIndex(SelectedRow))
        {
            if(PlayerOwner->WasInputKeyJustPressed(EKeys::T)) Inventory->RequestTransfer(Items[SelectedRow].Id,1,!bSelectContainer);
            if(!bSelectContainer && PlayerOwner->WasInputKeyJustPressed(EKeys::G)) Inventory->RequestDrop(Items[SelectedRow].Id,1);
            if(!bSelectContainer && PlayerOwner->WasInputKeyJustPressed(EKeys::F))
                if(auto* PC=Cast<ARVPlayerController>(PlayerOwner)) PC->RequestRefuel(Items[SelectedRow].Id,Items[SelectedRow].FuelRevision);
            if(!bSelectContainer && Needs && PlayerOwner->WasInputKeyJustPressed(EKeys::C)) Needs->RequestConsume(Items[SelectedRow].Id);
        }
        const float UIScale=FMath::Min(1.f,FMath::Min((Canvas->ClipX-30.f)/720.f,(Canvas->ClipY-100.f)/420.f));
        auto InventoryText=[&](const FString& Text,FLinearColor Color,float X,float Y)
        { DrawText(Text,Color,X*UIScale,Y*UIScale,nullptr,UIScale); };
        DrawRect(FLinearColor(0,0,0,.8f),15*UIScale,85*UIScale,720*UIScale,420*UIScale);
        InventoryText(TEXT("Inventory | Tab: panel  Up/Down: item  T: transfer  G: drop  C: consume  F: refuel  I: toggle"),FLinearColor::White,25,95);
        InventoryText(Inventory->Feedback,FLinearColor::Yellow,25,120);
        auto Panel=[&](URVInventoryComponent* C,float X,bool Active)
        {
            if(!C) return;
            InventoryText(FString::Printf(TEXT("%s %.1f/%.1f kg | %.1f/%.1f L"),*C->DisplayName.ToString(),C->GetWeightKg(),C->MaxWeightKg,C->GetVolumeLitres(),C->MaxVolumeLitres),FLinearColor::White,X,150);
            const auto Records=C->GetItems();
            for(int32 Row=0;Row<Records.Num();++Row)
            {
                const auto& Item=Records[Row]; if(!Item.Definition) continue;
                const FString Fuel=Item.Definition->Fuel.bFuelContainer?FString::Printf(TEXT(" | %.2f L"),Item.FuelLitres):FString();
                InventoryText(FString::Printf(TEXT("%s%s x%d | %.0f%%%s"),Active && Row==SelectedRow?TEXT("> "):TEXT(""),*Item.Definition->DisplayName.ToString(),Item.Quantity,Item.Condition*100,*Fuel),FLinearColor::White,X,180+Row*22);
            }
        };
        Panel(Inventory,25,!bSelectContainer); Panel(Inventory->OpenContainer,380,bSelectContainer);
    }
}
