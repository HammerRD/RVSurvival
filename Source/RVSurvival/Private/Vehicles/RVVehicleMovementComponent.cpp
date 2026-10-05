#include "Vehicles/RVVehicleMovementComponent.h"
#include "Components/PrimitiveComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "PhysicsEngine/BodyInstance.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/ConstraintInstance.h"
bool URVVehicleMovementComponent::ShouldCreatePhysicsState() const
{
    // The async vehicle manager submits simulations independently of GT ticks.
    // Proxies need the mesh rigid body for replication, but no vehicle simulation.
    return GetNetMode() != NM_Client && Super::ShouldCreatePhysicsState();
}
void URVVehicleMovementComponent::FixupSkeletalMesh()
{
    if (GetNetMode() != NM_Client) { Super::FixupSkeletalMesh(); return; }
    // Manager tick guards do not disable the suspension's independent Chaos
    // constraints. Proxies receive server rigid-body motion and must not apply
    // local suspension forces against stale/uninitialized wheel trace targets.
    // Skip native suspension creation on proxies, retaining wheel-body cleanup
    // through public component APIs. The chassis remains a replicated rigid body.
    if (auto* Mesh = GetSkeletalMesh())
    {
        for (const auto& Wheel : WheelSetups)
            if (auto* Body = Mesh->GetBodyInstance(Wheel.BoneName))
            {
                Body->SetResponseToAllChannels(ECR_Ignore);
                Body->SetInstanceSimulatePhysics(false);
                // Preserve native cleanup for rigs with imported wheel joints.
                // Those joints must not pull the server-driven proxy chassis.
                if (auto* Asset = Mesh->GetPhysicsAsset())
                {
                    TArray<int32> WheelConstraints;
                    Asset->BodyFindConstraints(Asset->FindBodyIndex(Wheel.BoneName), WheelConstraints);
                    for (const int32 Index : WheelConstraints)
                        if (Mesh->Constraints.IsValidIndex(Index) && Mesh->Constraints[Index])
                            Mesh->Constraints[Index]->TermConstraint();
                }
            }
        Mesh->KinematicBonesUpdateType = EKinematicBonesUpdateToPhysics::SkipSimulatingBones;
    }
}
void URVVehicleMovementComponent::BeginPlay()
{
    Super::BeginPlay();
    // Clients receive native rigid-body replication; no client vehicle force simulation.
    SetComponentTickEnabled(GetOwner()->HasAuthority());
    if (!GetOwner()->HasAuthority())
    {
        // Also cover physics state created before the actor acquired its net role.
        DestroyPhysicsState();
        FixupSkeletalMesh();
    }
    // A proxy has no suspension simulation to balance gravity. Let replicated
    // server rigid-body state supply its vertical motion, including parked sleep.
    if (!GetOwner()->HasAuthority() && UpdatedPrimitive)
        UpdatedPrimitive->SetEnableGravity(false);
    SetRequiresControllerForInputs(false);
}
void URVVehicleMovementComponent::PreTickGT(float DeltaTime)
{
    // Chaos' world vehicle manager calls this independently of component ticking.
    if (GetOwner()->HasAuthority()) Super::PreTickGT(DeltaTime);
}
void URVVehicleMovementComponent::Update(float DeltaTime)
{
    if (GetOwner()->HasAuthority()) Super::Update(DeltaTime);
}
void URVVehicleMovementComponent::ServerUpdateState_Implementation(float, float, float, float, int32, float, float, float)
{
    // The inherited RPC cannot inject raw values. Only the server's processed inputs
    // populate Chaos replicated state (including sleep/wake and transmission state).
    Super::ServerUpdateState_Implementation(SteeringInput, ThrottleInput, BrakeInput, HandbrakeInput,
        GetCurrentGear(), RollInput, PitchInput, YawInput);
}
