#include "UI/RVPrototypeHUD.h"
#include "Player/RVSurvivorCharacter.h"
#include "Interaction/RVInteractionComponent.h"
#include "Engine/Canvas.h"
#include "GameFramework/PlayerController.h"
#include "Player/RVPlayerController.h"
#include "Vehicles/RVVehicleBase.h"
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
        DrawText(Pawn->GetInteraction()->GetPrompt().ToString(), FLinearColor::White,
            Canvas->ClipX * 0.5f - 150.f, Canvas->ClipY * 0.5f + 35.f);
}
