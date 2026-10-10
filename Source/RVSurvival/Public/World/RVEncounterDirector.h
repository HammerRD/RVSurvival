#pragma once
#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "World/RVEncounterProfile.h"
#include "RVEncounterDirector.generated.h"
USTRUCT()
struct FRVRegionInfectedSnapshot
{
 GENERATED_BODY()
 UPROPERTY(SaveGame) FVector Position=FVector::ZeroVector;
 UPROPERTY(SaveGame) float Vitality=65;
 UPROPERTY(SaveGame) bool bDead=false;
 UPROPERTY(SaveGame) bool bLegInjured=false;
};
USTRUCT()
struct FRVEncounterSnapshot
{
 GENERATED_BODY()
 UPROPERTY(SaveGame) bool bSelected=false;
 UPROPERTY(SaveGame) ERVEncounterOutcome Outcome=ERVEncounterOutcome::Quiet;
 UPROPERTY(SaveGame) TArray<FRVRegionInfectedSnapshot> Infected;
};
/** Authority-only session pacing/population registry. No strong actor or world cache. */
UCLASS()
class RVSURVIVAL_API URVEncounterDirector : public UWorldSubsystem
{
 GENERATED_BODY()
public:
 UPROPERTY() TMap<FGuid,FRVEncounterSnapshot> Encounters;
 TMap<FGuid,TWeakObjectPtr<AActor>> Zones;
 TArray<TWeakObjectPtr<class ARVInfected>> ActiveInfected;
 int32 MaximumActiveInfected=12;
 double NextEventTime=0;
 TArray<ERVEncounterOutcome> Recent;
 bool Claim(FGuid Id,AActor* Zone);
 void Release(FGuid Id,AActor* Zone);
 int32 ActiveCount();
 FRVEncounterSnapshot& SelectAuthority(FGuid Id,const URVEncounterProfile* Profile,const TArray<FVector>& Positions);
};
