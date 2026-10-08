#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "RVCombatContentLibrary.generated.h"
/** Editor/development bridge to native engine tools; not a shipping spawn director. */
UCLASS()
class RVSURVIVAL_API URVCombatContentLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly,WorldContext="Context")) static bool BuildNavigationEditor(UObject* Context);
    UFUNCTION(BlueprintPure,meta=(DevelopmentOnly,WorldContext="Context")) static TMap<FString,FString> InspectNavigation(UObject* Context);
};
