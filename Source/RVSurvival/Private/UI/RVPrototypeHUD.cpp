#include "UI/RVPrototypeHUD.h"
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
void ARVPrototypeHUD::DrawHUD()
{
    Super::DrawHUD();
    if (!Canvas || !PlayerOwner) return;
    auto* PS=PlayerOwner->GetPlayerState<ARVPlayerState>();
    auto* Needs=PS?PS->Needs.Get():nullptr;
    if(Needs)
    {
        DrawText(FString::Printf(TEXT("Nutrition %.0f | Hydration %.0f | Fatigue %.0f"),Needs->State.Nutrition,Needs->State.Hydration,Needs->State.Fatigue),FLinearColor::White,20,Canvas->ClipY-40);
        DrawText(Needs->GetWarnings()+TEXT("  ")+Needs->Feedback,FLinearColor::Yellow,20,Canvas->ClipY-22);
        if(PlayerOwner->WasInputKeyJustPressed(EKeys::R)) Needs->RequestRestMode(ERVRestMode::Awake);
        if(PlayerOwner->WasInputKeyJustPressed(EKeys::Z)) Needs->RequestRestMode(Needs->State.RestMode==ERVRestMode::Sleeping?ERVRestMode::Resting:ERVRestMode::Sleeping);
    }
    DrawText(TEXT("+"), FLinearColor::White, Canvas->ClipX * 0.5f, Canvas->ClipY * 0.5f);
    if (const auto* PC = Cast<ARVPlayerController>(PlayerOwner); PC && PC->SeatedVehicle)
    {
        const bool Driver = PlayerOwner->GetPawn() == PC->SeatedVehicle;
        DrawText(Driver ? TEXT("PROTOTYPE RV | W: accelerate  S: brake/reverse  A/D: steer  Space: handbrake  E: exit when stopped")
            : TEXT("RV passenger | E: exit when stopped"), FLinearColor::White, 20, 35);
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
            if(!bSelectContainer && Needs && PlayerOwner->WasInputKeyJustPressed(EKeys::C)) Needs->RequestConsume(Items[SelectedRow].Id);
        }
        const float UIScale=FMath::Min(1.f,FMath::Min((Canvas->ClipX-30.f)/720.f,(Canvas->ClipY-100.f)/420.f));
        auto InventoryText=[&](const FString& Text,FLinearColor Color,float X,float Y)
        { DrawText(Text,Color,X*UIScale,Y*UIScale,nullptr,UIScale); };
        DrawRect(FLinearColor(0,0,0,.8f),15*UIScale,85*UIScale,720*UIScale,420*UIScale);
        InventoryText(TEXT("Inventory | Tab: panel  Up/Down: item  T: transfer  G: drop  C: consume  I: toggle"),FLinearColor::White,25,95);
        InventoryText(Inventory->Feedback,FLinearColor::Yellow,25,120);
        auto Panel=[&](URVInventoryComponent* C,float X,bool Active)
        {
            if(!C) return;
            InventoryText(FString::Printf(TEXT("%s %.1f/%.1f kg | %.1f/%.1f L"),*C->DisplayName.ToString(),C->GetWeightKg(),C->MaxWeightKg,C->GetVolumeLitres(),C->MaxVolumeLitres),FLinearColor::White,X,150);
            const auto Records=C->GetItems();
            for(int32 Row=0;Row<Records.Num();++Row)
            {
                const auto& Item=Records[Row]; if(!Item.Definition) continue;
                InventoryText(FString::Printf(TEXT("%s%s x%d | %.0f%%"),Active && Row==SelectedRow?TEXT("> "):TEXT(""),*Item.Definition->DisplayName.ToString(),Item.Quantity,Item.Condition*100),FLinearColor::White,X,180+Row*22);
            }
        };
        Panel(Inventory,25,!bSelectContainer); Panel(Inventory->OpenContainer,380,bSelectContainer);
    }
}
