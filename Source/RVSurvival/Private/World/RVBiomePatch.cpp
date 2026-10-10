#include "World/RVBiomePatch.h"
#include "Components/BoxComponent.h"
#include "PCGComponent.h"
ARVBiomePatch::ARVBiomePatch()
{
    Bounds=CreateDefaultSubobject<UBoxComponent>(TEXT("Bounds"));SetRootComponent(Bounds);
    Bounds->SetBoxExtent(FVector(10000,10000,10000));Bounds->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Bounds->SetMobility(EComponentMobility::Static);
    Dressing=CreateDefaultSubobject<UPCGComponent>(TEXT("Dressing"));
    Dressing->GenerationTrigger=EPCGComponentGenerationTrigger::GenerateOnDemand;
    Dressing->bIsComponentPartitioned=true;
}
