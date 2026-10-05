#include "UI/RVPrototypeHUD.h"
#include "Player/RVSurvivorCharacter.h"
#include "Interaction/RVInteractionComponent.h"
#include "Engine/Canvas.h"
#include "GameFramework/PlayerController.h"
#include "Player/RVPlayerController.h"
#include "Vehicles/RVVehicleBase.h"
#include "Inventory/RVInventoryComponent.h"
#include "InputCoreTypes.h"
void ARVPrototypeHUD::DrawHUD()
{
    Super::DrawHUD();
    if (!Canvas || !PlayerOwner) return;
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
        if(PlayerOwner->WasInputKeyJustPressed(EKeys::I)) bInventoryVisible=!bInventoryVisible;
        if(Inventory->OpenContainer) bInventoryVisible=true;
        if(!bInventoryVisible) { DrawText(TEXT("I: inventory"),FLinearColor::White,20,65); return; }
        if(PlayerOwner->WasInputKeyJustPressed(EKeys::Tab)) { bSelectContainer=!bSelectContainer; SelectedRow=0; }
        if(PlayerOwner->WasInputKeyJustPressed(EKeys::Down)) ++SelectedRow;
        if(PlayerOwner->WasInputKeyJustPressed(EKeys::Up)) --SelectedRow;
        auto* Selected=bSelectContainer?Inventory->OpenContainer.Get():Inventory;
        const TArray<FRVItemInstance> Items=Selected?Selected->GetItems():TArray<FRVItemInstance>();
        SelectedRow=FMath::Clamp(SelectedRow,0,FMath::Max(0,Items.Num()-1));
        if(Items.IsValidIndex(SelectedRow))
        {
            if(PlayerOwner->WasInputKeyJustPressed(EKeys::T)) Inventory->ServerTransfer(Items[SelectedRow].Id,1,!bSelectContainer);
            if(!bSelectContainer && PlayerOwner->WasInputKeyJustPressed(EKeys::G)) Inventory->ServerDrop(Items[SelectedRow].Id,1);
        }
        DrawRect(FLinearColor(0,0,0,.8),15,85,720,420);
        DrawText(TEXT("Inventory | Tab: panel  Up/Down: item  T: transfer one  G: drop one  I: toggle"),FLinearColor::White,25,95);
        DrawText(Inventory->Feedback,FLinearColor::Yellow,25,120);
        auto Panel=[&](URVInventoryComponent* C,float X,bool Active)
        {
            if(!C) return;
            DrawText(FString::Printf(TEXT("%s %.1f/%.1f kg | %.1f/%.1f L"),*C->DisplayName.ToString(),C->GetWeightKg(),C->MaxWeightKg,C->GetVolumeLitres(),C->MaxVolumeLitres),FLinearColor::White,X,150);
            const auto Records=C->GetItems();
            for(int32 Row=0;Row<Records.Num();++Row)
            {
                const auto& Item=Records[Row]; if(!Item.Definition) continue;
                DrawText(FString::Printf(TEXT("%s%s x%d | %.0f%%"),Active && Row==SelectedRow?TEXT("> "):TEXT(""),*Item.Definition->DisplayName.ToString(),Item.Quantity,Item.Condition*100),FLinearColor::White,X,180+Row*22);
            }
        };
        Panel(Inventory,25,!bSelectContainer); Panel(Inventory->OpenContainer,380,bSelectContainer);
    }
}
