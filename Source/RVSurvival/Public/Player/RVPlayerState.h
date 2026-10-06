#pragma once
#include "CoreMinimal.h"
#include "GameFramework/PlayerState.h"
#include "RVPlayerState.generated.h"
class URVNeedsComponent;
/** Gate 1 framework boundary; later gates add only the state owned by this role. */
UCLASS()
class RVSURVIVAL_API ARVPlayerState : public APlayerState
{
    GENERATED_BODY()
public:
    ARVPlayerState();
    virtual void CopyProperties(APlayerState* Destination) override;
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<URVNeedsComponent> Needs;
};
