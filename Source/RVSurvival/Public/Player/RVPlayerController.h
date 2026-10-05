#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "RVPlayerController.generated.h"
/** Gate 1 framework boundary; later gates add only the state owned by this role. */
UCLASS()
class RVSURVIVAL_API ARVPlayerController : public APlayerController
{
    GENERATED_BODY()
};
