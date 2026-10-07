#include "UI/RVPrototypeHUD.h"
#include "UI/RVMechanicalWidget.h"
#include "Blueprint/WidgetLayoutLibrary.h"
#include "Mechanical/RVServicePoint.h"
#include "Vehicles/RVMechanicalMotorhome.h"
#include "Player/RVPassengerReferenceFrameComponent.h"
#include "Vehicles/RVSystemsMotorhome.h"
#include "Vehicles/RVResourcePoint.h"
#include "Resources/RVElectricalComponent.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVLadderClimbComponent.h"
#include "Vehicles/RVVehicleSeatComponent.h"
#include "Interaction/RVInteractionComponent.h"
#include "Engine/Canvas.h"
#include "GameFramework/PlayerController.h"
#include "Player/RVPlayerController.h"
#include "Player/RVInputMappings.h"
#include "Vehicles/RVVehicleBase.h"
#include "Inventory/RVInventoryComponent.h"
#include "InputCoreTypes.h"
#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
#include "UI/RVSurvivalWidget.h"
void ARVPrototypeHUD::EndPlay(const EEndPlayReason::Type Reason)
{
    if(SurvivalWidget) { SurvivalWidget->RemoveFromParent(); SurvivalWidget=nullptr; }
    if(MechanicalWidget){MechanicalWidget->RemoveFromParent();MechanicalWidget=nullptr;}
    Super::EndPlay(Reason);
}
void ARVPrototypeHUD::DrawHUD()
{
    Super::DrawHUD();
    if (!Canvas || !PlayerOwner) return;
    const auto* MechanicalPC=Cast<ARVPlayerController>(PlayerOwner);
    AActor* MechanicalVehicle=MechanicalPC && MechanicalPC->MechanicalPoint?MechanicalPC->MechanicalPoint->Vehicle.Get():MechanicalPC?Cast<ARVMechanicalMotorhome>(MechanicalPC->SeatedVehicle.Get()):nullptr;
    if(!MechanicalVehicle && PlayerOwner->GetPawn())if(const auto* Frame=PlayerOwner->GetPawn()->FindComponentByClass<URVPassengerReferenceFrameComponent>())MechanicalVehicle=Cast<ARVMechanicalMotorhome>(Frame->ReferenceFrame.Get());
    if(MechanicalVehicle && !MechanicalWidget && PlayerOwner->IsLocalController())
    {MechanicalWidget=CreateWidget<URVMechanicalWidget>(PlayerOwner,URVMechanicalWidget::StaticClass());MechanicalWidget->AddToPlayerScreen();}
    // Collapsed UMG widgets do not tick: the HUD owns availability/visibility so
    // a panel first opened after spawn can never stay permanently collapsed.
    if(MechanicalWidget)
    {
        MechanicalWidget->SetVisibility(MechanicalVehicle?ESlateVisibility::HitTestInvisible:ESlateVisibility::Collapsed);
        const float Scale=UWidgetLayoutLibrary::GetViewportScale(PlayerOwner);
        const float Height=FMath::Max(100.f,MechanicalWidget->GetDesiredSize().Y*Scale);
        const float PreferredTop=MechanicalPC && (MechanicalPC->SeatedVehicle || MechanicalPC->ResourcePoint)?380.f:110.f;
        const float Top=FMath::Clamp(PreferredTop,20.f,FMath::Max(20.f,Canvas->ClipY-Height-20.f));
        MechanicalWidget->SetPositionInViewport(FVector2D(-20,Top),true);
        MechanicalWidget->SetAnchorsInViewport(FAnchors(1,0));
        MechanicalWidget->SetAlignmentInViewport(FVector2D(1,0));
    }
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
    }
    if(auto* PC=Cast<ARVPlayerController>(PlayerOwner))
    {
        auto* V=PC->ResourcePoint?PC->ResourcePoint->Vehicle.Get():Cast<ARVSystemsMotorhome>(PC->SeatedVehicle.Get());
        if(V)
        {
            auto* Bus=V->Electrical.Get();
            const float X=FMath::Max(20.f,Canvas->ClipX-370.f);
            DrawRect(FLinearColor(0,0,0,.75f),X,110,350,245);
            DrawText(FString::Printf(TEXT("RV monitor | Fuel %.2f / %.0f L"),V->PropulsionFuel->Litres,V->PropulsionFuel->CapacityLitres),FLinearColor::White,X+10,120,nullptr,.85f);
            DrawText(FString::Printf(TEXT("House %.0f%% (%.1f Wh) | Chassis %.0f%%"),V->HouseBattery->GetStateOfCharge()*100,V->HouseBattery->EnergyWh,V->ChassisBattery->GetStateOfCharge()*100),FLinearColor::White,X+10,145,nullptr,.8f);
            DrawText(FString::Printf(TEXT("Generator %s | solar %.0f%% | idle %s"),Bus->bGeneratorRunning?TEXT("ON"):TEXT("off"),Bus->SolarInput*100,Bus->bEngineIdleRequested?TEXT("ON"):TEXT("off")),FLinearColor::White,X+10,170,nullptr,.8f);
            DrawText(FString::Printf(TEXT("Load %.0f/%.0f W | battery %+.0f W"),Bus->Flow.SuppliedWatts,Bus->Flow.RequestedWatts,Bus->Flow.HouseBatteryWatts),FLinearColor::White,X+10,195,nullptr,.8f);
            int32 Line=0;
            for(const auto& Load:Bus->Loads) DrawText(FString::Printf(TEXT("%s: %s / %s"),*Load.DisplayName.ToString(),Load.bEnabled?TEXT("on"):TEXT("off"),Load.bPowered?TEXT("powered"):TEXT("no power")),FLinearColor::White,X+10,220+(Line++)*18,nullptr,.75f);
            DrawText(Bus->GetSourceSummary(),FLinearColor::White,X+10,288,nullptr,.7f);
            DrawText(PC->ResourceFeedback,FLinearColor::Yellow,X+10,310,nullptr,.75f);
            if(PC->ResourcePoint && !PC->ResourcePoint->bFuelFill)
            {
                DrawText(TEXT("H lights | J generator | K fridge | L tools | O idle"),FLinearColor::White,X+10,333,nullptr,.7f);
            }
        }
    }
    DrawText(TEXT("+"), FLinearColor::White, Canvas->ClipX * 0.5f, Canvas->ClipY * 0.5f);
    if (const auto* PC = Cast<ARVPlayerController>(PlayerOwner); PC && PC->SeatedVehicle)
    {
        const bool Driver = PlayerOwner->GetPawn() == PC->SeatedVehicle;
        const auto* Character=Cast<ARVSurvivorCharacter>(PlayerOwner->GetPawn());
        const auto* Seat=Character?Cast<URVVehicleSeatComponent>(Character->GetRootComponent()->GetAttachParent()):nullptr;
        DrawText(Driver ? TEXT("PROTOTYPE RV | W: accelerate  S: brake/reverse  A/D: steer  Space: handbrake  E: exit when stopped")
            : Seat && Seat->bInteriorOnly ? TEXT("RV living-area seat | E: stand in aisle") : TEXT("RV passenger | E: exit when stopped"), FLinearColor::White, 20, 35);
        DrawText(FString::Printf(TEXT("%s driver | %s passenger | %s next seat (stopped) | %s living area | %s Controls"),
            *RVInputMappings::KeyLabel(PlayerOwner,TEXT("DriverSeat"),TEXT("1")),
            *RVInputMappings::KeyLabel(PlayerOwner,TEXT("PassengerSeat"),TEXT("2")),
            *RVInputMappings::KeyLabel(PlayerOwner,TEXT("NextSeat"),TEXT("V")),
            *RVInputMappings::KeyLabel(PlayerOwner,TEXT("RearInterior"),TEXT("3")),
            *RVInputMappings::KeyLabel(PlayerOwner,TEXT("Controls"),TEXT("F10"))), FLinearColor::White, 20, 60);
        DrawText(PC->SeatFeedback, FLinearColor::Yellow, 20, 85);
        return;
    }
    if (const auto* Pawn = Cast<ARVSurvivorCharacter>(PlayerOwner->GetPawn()))
    {
        if(const auto* Climb=Pawn->FindComponentByClass<URVLadderClimbComponent>();Climb && Climb->Ladder)
        { DrawText(TEXT("Ladder | climb up/down | interact: dismount at ground or supported roof | F10 Controls"),FLinearColor::White,20,35); return; }
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
                if(auto* PC=Cast<ARVPlayerController>(PlayerOwner))
                {if(PC->MechanicalPoint)PC->RequestService(TEXT("Refill"),PC->MechanicalPoint->Revision,Items[SelectedRow].Id,Items[SelectedRow].FuelRevision);else PC->RequestRefuel(Items[SelectedRow].Id,Items[SelectedRow].FuelRevision);}
            if(!bSelectContainer && Needs && PlayerOwner->WasInputKeyJustPressed(EKeys::C)) Needs->RequestConsume(Items[SelectedRow].Id);
        }
        const float UIScale=FMath::Min(1.f,FMath::Min((Canvas->ClipX-30.f)/720.f,(Canvas->ClipY-100.f)/420.f));
        auto InventoryText=[&](const FString& Text,FLinearColor Color,float X,float Y)
        { DrawText(Text,Color,X*UIScale,Y*UIScale,nullptr,UIScale); };
        DrawRect(FLinearColor(0,0,0,.8f),15*UIScale,85*UIScale,720*UIScale,420*UIScale);
        const auto* ServicePC=Cast<ARVPlayerController>(PlayerOwner);
        InventoryText(ServicePC && ServicePC->MechanicalPoint ? TEXT("Inventory | Tab: panel  Up/Down: item  T: transfer  G: drop  C: consume  F: coolant  I: toggle") : TEXT("Inventory | Tab: panel  Up/Down: item  T: transfer  G: drop  C: consume  F: refuel  I: toggle"),FLinearColor::White,25,95);
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
