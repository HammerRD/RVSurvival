#pragma once
#include "CoreMinimal.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "RVCharacterMovementComponent.generated.h"
/** Native movement/prediction unchanged; development diagnostics for moving-platform validation. */
UCLASS()
class RVSURVIVAL_API URVCharacterMovementComponent : public UCharacterMovementComponent
{
    GENERATED_BODY()
public:
    virtual float GetMaxSpeed() const override;
protected:
    virtual void OnClientCorrectionReceived(FNetworkPredictionData_Client_Character& ClientData, float TimeStamp, FVector NewLocation, FVector NewVelocity, FMovementBaseInterfaceData* NewBase, FName Bone, bool bHasBase, bool bRelative, uint8 Mode, FVector Gravity) override;
};
