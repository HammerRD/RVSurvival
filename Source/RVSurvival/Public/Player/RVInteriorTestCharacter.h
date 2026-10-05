#pragma once
#include "CoreMinimal.h"
#include "Player/RVSurvivorCharacter.h"
#include "RVInteriorTestCharacter.generated.h"

/** Visible, collision-free test presentation for Gate 3 observer validation only. */
UCLASS()
class RVSURVIVAL_API ARVInteriorTestCharacter : public ARVSurvivorCharacter
{
    GENERATED_BODY()
public:
    ARVInteriorTestCharacter(const FObjectInitializer& Initializer);
private:
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UStaticMeshComponent> PrototypeTorso;
    UPROPERTY(VisibleAnywhere) TObjectPtr<class UStaticMeshComponent> PrototypeHead;
};
