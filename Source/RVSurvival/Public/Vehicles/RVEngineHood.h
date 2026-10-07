#pragma once
#include "CoreMinimal.h"
#include "Vehicles/RVInteractiveDoor.h"
#include "RVEngineHood.generated.h"
/** Same supported replicated hinge, with engine-service movement safety. */
UCLASS()
class RVSURVIVAL_API ARVEngineHood : public ARVInteractiveDoor
{
    GENERATED_BODY()
public:
    virtual bool CanInteract_Implementation(APawn* Pawn)const override
    {return Super::CanInteract_Implementation(Pawn) && GetOwner() && GetOwner()->GetVelocity().Size()<10;}
};
