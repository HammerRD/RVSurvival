#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "World/RVEncounterProfile.h"
#include "RVRegionEncounterZone.generated.h"
/** Authored context/spawn anchors. Native timers, nav projection, RPC replication and AI. */
UCLASS()
class RVSURVIVAL_API ARVRegionEncounterZone : public AActor
{
 GENERATED_BODY()
public:
 ARVRegionEncounterZone();
 virtual void BeginPlay() override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
 virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
 UPROPERTY(EditAnywhere,BlueprintReadOnly,SaveGame) FGuid ZoneId;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) TObjectPtr<URVEncounterProfile> Profile;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) TArray<FVector> SpawnOffsets;
 UPROPERTY(EditAnywhere,BlueprintReadOnly) TSubclassOf<class ARVScavengeContainer> SupplyCacheClass;
 UPROPERTY(Replicated,BlueprintReadOnly) ERVEncounterOutcome Outcome=ERVEncounterOutcome::Quiet;
 UPROPERTY(Replicated,BlueprintReadOnly) bool bEvaluated=false;
private:
 void UpdateAuthority();
 void SuspendAuthority();
 bool IsSafeSpawn(const FVector& Position,float Radius,float HalfHeight) const;
 bool bOwnsIdentity=false;
 bool bActive=false;
 FTimerHandle UpdateTimer;
 TMap<int32,TWeakObjectPtr<class ARVInfected>> Members;
 TWeakObjectPtr<class ARVScavengeContainer> Cache;
};
