#pragma once
#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "RVGameInstance.generated.h"
/** Gate 1 framework boundary; later gates add only the state owned by this role. */
UCLASS()
class RVSURVIVAL_API URVGameInstance : public UGameInstance
{
    GENERATED_BODY()
};
