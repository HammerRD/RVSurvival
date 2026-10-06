#pragma once
#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "RVPrototypeHUD.generated.h"
/** Temporary asset-free Gate 1 prompt. Queries gameplay; owns no rules. Replace with UMG presentation. */
UCLASS()
class RVSURVIVAL_API ARVPrototypeHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
    virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
    UPROPERTY(Transient) TObjectPtr<class URVSurvivalWidget> SurvivalWidget;
    bool bInventoryVisible = false;
    bool bSelectContainer = false;
    int32 SelectedRow = 0;
    TWeakObjectPtr<class URVInventoryComponent> LastContainer;
};
