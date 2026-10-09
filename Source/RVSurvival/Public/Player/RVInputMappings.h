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
    FString KeyLabel(APlayerController* Controller,FName Name,const TCHAR* Fallback);
    FName Category(FName Name);
    FKey CurrentKey(APlayerController* Controller,FName Name,FKey Fallback);
}
