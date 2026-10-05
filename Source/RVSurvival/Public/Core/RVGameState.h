#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameStateBase.h"
#include "RVGameState.generated.h"
/** Gate 1 framework boundary; later gates add only the state owned by this role. */
UCLASS()
class RVSURVIVAL_API ARVGameState : public AGameStateBase
{
    GENERATED_BODY()
};
