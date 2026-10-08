#pragma once
#include "CoreMinimal.h"
#include "GameplayEffect.h"
#include "RVAnalgesicEffect.generated.h"

/** Native, network-addressable effect class. Duration/magnitude come from item metadata. */
UCLASS()
class RVSURVIVAL_API URVAnalgesicEffect : public UGameplayEffect
{
    GENERATED_BODY()
public:
    URVAnalgesicEffect();
};
