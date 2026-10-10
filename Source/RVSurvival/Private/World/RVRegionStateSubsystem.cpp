#include "World/RVRegionStateSubsystem.h"
#include "Engine/World.h"
bool URVRegionStateSubsystem::Claim(FGuid Id,AActor* Actor)
{
    if(!Id.IsValid() || !IsValid(Actor) || !Actor->HasAuthority()) return false;
    if(const auto* Existing=ActiveContainers.Find(Id))
        if(Existing->IsValid() && Existing->Get()!=Actor) return false;
    ActiveContainers.Add(Id,Actor);return true;
}
void URVRegionStateSubsystem::Release(FGuid Id,AActor* Actor)
{
    if(const auto* Existing=ActiveContainers.Find(Id))
        if(Existing->Get()==Actor) ActiveContainers.Remove(Id);
}
