#include "UI/RVPrototypeHUD.h"
#include "Player/RVSurvivorCharacter.h"
#include "Interaction/RVInteractionComponent.h"
#include "Engine/Canvas.h"
#include "GameFramework/PlayerController.h"
void ARVPrototypeHUD::DrawHUD()
{
    Super::DrawHUD();
    if (!Canvas || !PlayerOwner) return;
    DrawText(TEXT("+"), FLinearColor::White, Canvas->ClipX * 0.5f, Canvas->ClipY * 0.5f);
    if (const auto* Pawn = Cast<ARVSurvivorCharacter>(PlayerOwner->GetPawn()))
        DrawText(Pawn->GetInteraction()->GetPrompt().ToString(), FLinearColor::White,
            Canvas->ClipX * 0.5f - 150.f, Canvas->ClipY * 0.5f + 35.f);
}
