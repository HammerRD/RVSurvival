#pragma once
#include "CoreMinimal.h"
#include "InputCoreTypes.h"
class UInputAction;
class UInputMappingContext;
class APlayerController;
class ULocalPlayer;
/** Labels/registration only; persistence and rebinding remain EnhancedInput-owned. */
namespace RVInputMappings
{
    void Map(UInputMappingContext* Context,UInputAction* Action,FKey Key,FName Name,const TCHAR* Label);
    void Register(APlayerController* Controller,UInputMappingContext* Context);
    void Unregister(ULocalPlayer* Local,UInputMappingContext* Context);
}
