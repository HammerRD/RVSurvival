#include "Core/RVGameMode.h"
#include "UI/RVPrototypeHUD.h"
#include "Core/RVGameState.h"
#include "Player/RVPlayerController.h"
#include "Player/RVPlayerState.h"
#include "Player/RVSurvivorCharacter.h"
ARVGameMode::ARVGameMode()
{
    HUDClass = ARVPrototypeHUD::StaticClass();
    DefaultPawnClass = ARVSurvivorCharacter::StaticClass();
    PlayerControllerClass = ARVPlayerController::StaticClass();
    PlayerStateClass = ARVPlayerState::StaticClass();
    GameStateClass = ARVGameState::StaticClass();
}
