#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Net/Serialization/FastArraySerializer.h"
#include "Inventory/RVItemDefinition.h"
#include "RVInventoryComponent.generated.h"

USTRUCT(BlueprintType)
struct FRVItemStateEntry
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName Key;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FString Value;
};

USTRUCT(BlueprintType)
struct FRVItemInstance : public FFastArraySerializerItem
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadOnly) FGuid Id;
    UPROPERTY(BlueprintReadOnly) TObjectPtr<URVItemDefinition> Definition;
    UPROPERTY(BlueprintReadOnly) int32 Quantity = 1;
    UPROPERTY(BlueprintReadOnly) float Condition = 1;
    UPROPERTY(BlueprintReadOnly) FName Location = TEXT("Main");
    UPROPERTY(BlueprintReadOnly) TArray<FRVItemStateEntry> CustomState;
};

USTRUCT()
struct FRVInventoryList : public FFastArraySerializer
{
    GENERATED_BODY()
    UPROPERTY() TArray<FRVItemInstance> Items;
    bool NetDeltaSerialize(FNetDeltaSerializeInfo& Info)
    { return FastArrayDeltaSerialize<FRVItemInstance, FRVInventoryList>(Items, Info, *this); }
};
template<> struct TStructOpsTypeTraits<FRVInventoryList> : TStructOpsTypeTraitsBase2<FRVInventoryList>
{ enum { WithNetDeltaSerializer = true }; };

/** Authority-only transactions. Presentation never mutates the replicated list. */
UCLASS(ClassGroup=(RV), meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVInventoryComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    URVInventoryComponent();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float MaxWeightKg = 25;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) float MaxVolumeLitres = 35;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) bool bAllowPhysicalCarry = false;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FGameplayTagContainer AllowedTags;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FText DisplayName;
    UFUNCTION(BlueprintPure) TArray<FRVItemInstance> GetItems() const { return Contents.Items; }
    UFUNCTION(BlueprintPure) float GetWeightKg() const;
    UFUNCTION(BlueprintPure) float GetVolumeLitres() const;
    UFUNCTION(BlueprintPure) FString CanAccept(const FRVItemInstance& Item) const;
    bool AddAuthority(const FRVItemInstance& Item, FString& Error);
    bool TransferAuthority(URVInventoryComponent* Destination, const FGuid& Id, int32 Quantity, FString& Error);
    void OpenContainerAuthority(URVInventoryComponent* Container);
    UPROPERTY(Replicated, BlueprintReadOnly) TObjectPtr<URVInventoryComponent> OpenContainer;
    UPROPERTY(Replicated, BlueprintReadOnly) FString Feedback;
    UFUNCTION(Server, Reliable, BlueprintCallable) void ServerTransfer(FGuid Id, int32 Quantity, bool bToContainer);
    UFUNCTION(Server, Reliable, BlueprintCallable) void ServerDrop(FGuid Id, int32 Quantity);
protected:
    UPROPERTY(Replicated) FRVInventoryList Contents;
};

/** Shared cabinets use the same transaction and capacity implementation as player storage. */
UCLASS(ClassGroup=(RV), meta=(BlueprintSpawnableComponent))
class RVSURVIVAL_API URVContainerComponent : public URVInventoryComponent
{
    GENERATED_BODY()
public:
    URVContainerComponent() { MaxWeightKg = 100; MaxVolumeLitres = 120; bAllowPhysicalCarry = true; }
};
