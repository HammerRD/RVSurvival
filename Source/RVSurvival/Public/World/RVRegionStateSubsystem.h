#pragma once
#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "Inventory/RVInventoryComponent.h"
#include "RVRegionStateSubsystem.generated.h"

USTRUCT(BlueprintType)
struct FRVContainerSnapshot
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly, SaveGame) bool bGenerated=false;
    UPROPERTY(BlueprintReadOnly, SaveGame) bool bSearched=false;
    UPROPERTY(BlueprintReadOnly, SaveGame) TArray<FRVItemInstance> Items;
};

/** Authority-only session ledger survives streamed-cell unload, not world destruction.
 * Contains item data, not actor/world references. Full campaign saving is deferred. */
UCLASS()
class RVSURVIVAL_API URVRegionStateSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()
public:
    UPROPERTY() TMap<FGuid,FRVContainerSnapshot> Containers;
    TMap<FGuid,TWeakObjectPtr<AActor>> ActiveContainers;
    bool Claim(FGuid Id,AActor* Actor);
    void Release(FGuid Id,AActor* Actor);
};
