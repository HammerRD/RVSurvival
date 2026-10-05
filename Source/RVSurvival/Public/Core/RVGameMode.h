#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "RVGameMode.generated.h"
/** Server-only rules and spawning. */
UCLASS()
class RVSURVIVAL_API ARVGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    ARVGameMode();
};
