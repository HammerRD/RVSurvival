#include "Combat/RVCombatContentLibrary.h"
#include "NavigationSystem.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "NavMesh/RecastNavMesh.h"
bool URVCombatContentLibrary::BuildNavigationEditor(UObject* Context)
{
#if WITH_EDITOR
    auto* World=Context?Context->GetWorld():nullptr;if(!World || World->IsGameWorld())return false;
    if(auto* Nav=FNavigationSystem::GetCurrent<UNavigationSystemV1>(World)){Nav->Build();return true;}
#endif
    return false;
}
TMap<FString,FString> URVCombatContentLibrary::InspectNavigation(UObject* Context)
{
    TMap<FString,FString> Result;
#if WITH_EDITOR
    auto* World=Context?Context->GetWorld():nullptr;if(!World)return Result;
    for(TActorIterator<AStaticMeshActor> It(World);It;++It)if(It->GetActorLabel().Contains(TEXT("Ground")))
    {const auto* C=It->GetStaticMeshComponent();Result.Add(It->GetActorLabel(),FString::Printf(TEXT("navRelevant=%d collision=%s mobility=%d"),C->CanEverAffectNavigation(),*C->GetCollisionProfileName().ToString(),int32(C->Mobility)));}
    for(TActorIterator<ARecastNavMesh> It(World);It;++It)Result.Add(It->GetName(),FString::Printf(TEXT("tiles=%d radius=%.1f height=%.1f"),It->GetNavMeshTilesCount(),It->AgentRadius,It->AgentHeight));
#endif
    return Result;
}
