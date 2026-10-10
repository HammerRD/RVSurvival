#include "World/RVRegionGameMode.h"
#include "Vehicles/RVInteriorMotorhome.h"
#include "Player/RVSurvivorCharacter.h"
#include "Player/RVPassengerReferenceFrameComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/PrimitiveComponent.h"
#include "Components/WorldPartitionStreamingSourceComponent.h"
#include "EngineUtils.h"
#include "Engine/World.h"
#include "TimerManager.h"

void ARVRegionGameMode::BeginPlay()
{
    Super::BeginPlay();
    if(!HasAuthority() || !GetWorld()->GetWorldPartition())return;
    if(bKeepConnectionStartupNeighborhoodLoaded)
    {
        // Use the same native grid loading ranges as the initial client view at
        // world origin. This is a bounded region workaround for pending-join
        // visibility ordering, not a missing-package validation bypass.
        auto* StartupSource=NewObject<UWorldPartitionStreamingSourceComponent>(this,TEXT("ConnectionStartupStreamingSource"));
        AddInstanceComponent(StartupSource);StartupSource->RegisterComponent();
    }
    for(TActorIterator<ARVInteriorMotorhome> It(GetWorld());It;++It)
    {
        auto* Vehicle=*It;
        if(!Vehicle->ActorHasTag(MobileBaseTag) || Vehicle->FindComponentByClass<UWorldPartitionStreamingSourceComponent>())continue;
        auto* Source=NewObject<UWorldPartitionStreamingSourceComponent>(Vehicle,TEXT("MobileBaseStreamingSource"));
        FStreamingSourceShape Shape;Shape.bUseGridLoadingRange=false;
        Shape.Radius=FMath::Clamp(MobileBaseLoadingRadiusCm,5000.f,30000.f);
        Source->Shapes.Add(Shape);Vehicle->AddInstanceComponent(Source);Source->RegisterComponent();
    }
}

void ARVRegionGameMode::RestartPlayer(AController* NewPlayer)
{
    Super::RestartPlayer(NewPlayer);
    if(!bArriveAtMobileBase || !IsValid(NewPlayer) || !NewPlayer->GetPawn())return;
    const TWeakObjectPtr<AController> Player=NewPlayer;
    GetWorldTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Player]
    {if(Player.IsValid())PlaceAtMobileBase(Player.Get());}));
}
void ARVRegionGameMode::PlaceAtMobileBase(AController* Controller)
{
    auto* Character=Controller?Cast<ARVSurvivorCharacter>(Controller->GetPawn()):nullptr;
    if(!HasAuthority() || !Character || Character->SeatedVehicle)return;
    for(TActorIterator<ARVInteriorMotorhome> It(GetWorld());It;++It)
    {
        auto* Vehicle=*It;if(!Vehicle->ActorHasTag(MobileBaseTag))continue;
        // The accepted helper checks the real platform floor, furniture and other
        // capsules. Arrival happens once, never by forcing a passenger each tick.
        FVector Position;UPrimitiveComponent* Floor=nullptr;
        for(const FVector Preferred:{FVector(95,0,180),FVector(-120,0,180),FVector(-200,0,180)})
        {
            if(!Vehicle->FindSafeInteriorPosition(Character,Preferred,Position,Floor))continue;
            auto* Movement=Character->GetCharacterMovement();Movement->StopMovementImmediately();
            Character->SetActorLocation(Position,false,nullptr,ETeleportType::TeleportPhysics);
            Movement->SetMovementMode(MOVE_Walking);Movement->FindFloor(Position,Movement->CurrentFloor,false);
            auto BaseData=MovementBaseUtility::GetMovementBaseDataFromPhysicsOwner(Floor);
            Character->SetBase(&BaseData);
            if(auto* Frame=Character->FindComponentByClass<URVPassengerReferenceFrameComponent>())
                Frame->TickComponent(0,LEVELTICK_All,nullptr);
            Character->SetBase(&BaseData);Movement->Velocity=FVector::ZeroVector;Character->ForceNetUpdate();return;
        }
        UE_LOG(LogTemp,Warning,TEXT("Region arrival aisle unavailable; retaining safe native PlayerStart"));return;
    }
}
