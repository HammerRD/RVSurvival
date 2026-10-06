#include "Player/RVCharacterMovementComponent.h"
#include "Player/RVPassengerReferenceFrameComponent.h"
#include "GameFramework/Character.h"
#include "Player/RVPlayerState.h"
#include "Survival/RVNeedsComponent.h"
float URVCharacterMovementComponent::GetMaxSpeed() const
{
    const auto* PS=CharacterOwner?CharacterOwner->GetPlayerState<ARVPlayerState>():nullptr;
    return Super::GetMaxSpeed()*(PS && PS->Needs?PS->Needs->GetMovementScale():1.f);
}
void URVCharacterMovementComponent::OnClientCorrectionReceived(FNetworkPredictionData_Client_Character& Data, float Time, FVector Location, FVector NewVelocity, FMovementBaseInterfaceData* Base, FName Bone, bool bHasBase, bool bRelative, uint8 Mode, FVector Gravity)
{
    if (CharacterOwner)
        if (auto* Frame = CharacterOwner->FindComponentByClass<URVPassengerReferenceFrameComponent>())
        {
            // Compare the acknowledged saved move, not current predicted location (which is later in time).
            FVector Saved = Data.LastAckedMove.IsValid() ? Data.LastAckedMove->SavedLocation : CharacterOwner->GetActorLocation();
            FVector MetricLocation = Location;
            if (bRelative && Base && Data.LastAckedMove.IsValid()
                && Data.LastAckedMove->EndMovementBaseInterfaceData == *Base)
            {
                FVector Relative;
                if (MovementBaseUtility::TransformLocationToLocal(Base, Bone, Location, Relative))
                { Saved = Data.LastAckedMove->SavedRelativeLocation; MetricLocation = Relative; }
            }
            Frame->RecordCorrection(FVector::Distance(Saved, MetricLocation));
        }
    Super::OnClientCorrectionReceived(Data, Time, Location, NewVelocity, Base, Bone, bHasBase, bRelative, Mode, Gravity);
}
