#include "Inventory/RVInventoryComponent.h"
#include "Resources/RVFuelComponent.h"
#include "Net/UnrealNetwork.h"
#include "Inventory/RVWorldItem.h"
#include "GameFramework/Pawn.h"
#include "Engine/World.h"
#include "CollisionShape.h"
#include "Core/RVLog.h"
#include "HAL/IConsoleManager.h"
#include "TimerManager.h"
#include "Player/RVPlayerState.h"
#include "Medical/RVHealthComponent.h"
#include "GameFramework/Character.h"
#include "Components/CapsuleComponent.h"
static TAutoConsoleVariable<int32> InventoryDebug(TEXT("rv.Inventory.Debug"),0,TEXT("Log authoritative inventory requests"));
URVInventoryComponent::URVInventoryComponent() { SetIsReplicatedByDefault(true); DisplayName=FText::FromString(TEXT("Player storage")); }
void URVInventoryComponent::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{ Super::GetLifetimeReplicatedProps(OutLifetimeProps); DOREPLIFETIME(URVInventoryComponent, Contents); DOREPLIFETIME(URVInventoryComponent, MaxWeightKg); DOREPLIFETIME(URVInventoryComponent, MaxVolumeLitres); DOREPLIFETIME(URVInventoryComponent, bAllowPhysicalCarry); DOREPLIFETIME(URVInventoryComponent, AllowedTags); DOREPLIFETIME(URVInventoryComponent, DisplayName); DOREPLIFETIME_CONDITION(URVInventoryComponent, OpenContainer, COND_OwnerOnly); DOREPLIFETIME_CONDITION(URVInventoryComponent, Feedback, COND_OwnerOnly); }
float URVInventoryComponent::GetWeightKg() const
{ float Total=0; for(const auto& I:Contents.Items) if(I.Definition) Total+=I.Definition->WeightKg*I.Quantity; return Total; }
float URVInventoryComponent::GetVolumeLitres() const
{ float Total=0; for(const auto& I:Contents.Items) if(I.Definition) Total+=I.Definition->VolumeLitres*I.Quantity; return Total; }
FString URVInventoryComponent::CanAccept(const FRVItemInstance& I) const
{
    if(!FMath::IsFinite(MaxWeightKg) || !FMath::IsFinite(MaxVolumeLitres) || MaxWeightKg<0 || MaxVolumeLitres<0) return TEXT("Invalid storage capacity configuration");
    if(!I.Definition || !I.Id.IsValid() || I.Quantity<=0 || !FMath::IsFinite(I.Condition) || I.Condition<0 || I.Condition>1) return TEXT("Invalid item");
    const auto* D=I.Definition.Get();
    if(!FMath::IsFinite(D->WeightKg) || !FMath::IsFinite(D->VolumeLitres) || D->WeightKg<0 || D->VolumeLitres<0) return TEXT("Invalid definition");
    if(D->Fuel.bFuelContainer)
    {
        const auto& F=D->Fuel;
        if(D->bStackable || I.Quantity!=1 || !F.FuelType.IsValid() || !FMath::IsFinite(F.CapacityLitres) || F.CapacityLitres<=0
            || !FMath::IsFinite(F.InitialLitres) || F.InitialLitres<0 || F.InitialLitres>F.CapacityLitres
            || (I.bFuelInitialized && (!FMath::IsFinite(I.FuelLitres) || I.FuelLitres<0 || I.FuelLitres>F.CapacityLitres || I.FuelRevision<0)))
            return TEXT("Invalid fuel container state");
    }
    if(D->Combat.bMagazine || D->Combat.bFirearm)
    {
        const auto& C=D->Combat;
        if(D->bStackable || I.Quantity!=1 || !C.Caliber.IsValid() || C.bMagazine==C.bFirearm
            || C.MagazineCapacity<1 || C.InitialRounds<0 || C.InitialRounds>C.MagazineCapacity
            || I.CombatRevision<0 || (I.bMagazineInitialized && (I.MagazineRounds<0 || I.MagazineRounds>C.MagazineCapacity)))
            return TEXT("Invalid combat item state");
    }
    if(I.LoadedInWeapon.IsValid()) return TEXT("Unload magazine before moving it");
    if(I.Quantity>(D->bStackable?FMath::Max(1,D->MaxStackSize):1)) return TEXT("Invalid stack size");
    if(D->bRequiresPhysicalCarry && !bAllowPhysicalCarry) return TEXT("Requires physical carrying");
    if(!AllowedTags.IsEmpty() && !D->Tags.HasAny(AllowedTags)) return TEXT("Item category not allowed");
    if(GetWeightKg()+D->WeightKg*I.Quantity>MaxWeightKg+KINDA_SMALL_NUMBER) return TEXT("Weight capacity exceeded");
    if(GetVolumeLitres()+D->VolumeLitres*I.Quantity>MaxVolumeLitres+KINDA_SMALL_NUMBER) return TEXT("Volume capacity exceeded");
    for(const auto& Existing:Contents.Items) if(Existing.Id==I.Id) return TEXT("Duplicate item identity");
    return FString();
}
bool URVInventoryComponent::AddAuthority(const FRVItemInstance& Item, FString& Error)
{
    if(!GetOwner() || !GetOwner()->HasAuthority()) { Error=TEXT("Authority required"); return false; }
    Error=CanAccept(Item); if(!Error.IsEmpty()) return false;
    // Reset transport bookkeeping when a record changes owning FastArray.
    auto& Added=Contents.Items.AddDefaulted_GetRef();
    Added.Id=Item.Id; Added.Definition=Item.Definition; Added.Quantity=Item.Quantity;
    Added.Condition=Item.Condition; Added.Location=Item.Location; Added.CustomState=Item.CustomState;
    Added.bFuelInitialized=Item.bFuelInitialized; Added.FuelLitres=Item.FuelLitres; Added.FuelRevision=Item.FuelRevision;
    Added.bMagazineInitialized=Item.bMagazineInitialized; Added.MagazineRounds=Item.MagazineRounds;
    Added.CombatRevision=Item.CombatRevision; Added.LoadedInWeapon=Item.LoadedInWeapon;
    if(Added.Definition->Combat.bMagazine && !Added.bMagazineInitialized)
    { Added.bMagazineInitialized=true; Added.MagazineRounds=Added.Definition->Combat.InitialRounds; }
    if(Added.Definition->Fuel.bFuelContainer && !Added.bFuelInitialized)
    { Added.bFuelInitialized=true; Added.FuelLitres=Added.Definition->Fuel.InitialLitres; }
    Contents.MarkItemDirty(Added); GetOwner()->ForceNetUpdate(); return true;
}
bool URVInventoryComponent::TransferAuthority(URVInventoryComponent* Destination, const FGuid& Id, int32 Quantity, FString& Error)
{
    if(!GetOwner() || !GetOwner()->HasAuthority() || !Destination || Destination==this || !Destination->GetOwner() || !Destination->GetOwner()->HasAuthority())
    { Error=TEXT("Invalid authoritative destination"); return false; }
    const int32 Index=Contents.Items.IndexOfByPredicate([&](const auto& I){ return I.Id==Id; });
    if(Index==INDEX_NONE || Quantity<=0 || Quantity>Contents.Items[Index].Quantity) { Error=TEXT("Item no longer available"); return false; }
    FRVItemInstance Moving=Contents.Items[Index]; Moving.Quantity=Quantity;
    if(Moving.LoadedInWeapon.IsValid() || Contents.Items.ContainsByPredicate([&](const auto& I){return I.LoadedInWeapon==Id;}))
    {Error=TEXT("Unload weapon before transferring");return false;}
    if(Quantity<Contents.Items[Index].Quantity) Moving.Id=FGuid::NewGuid();
    // Both operations execute serially on the server game thread; no yield between validation and commit.
    if(!Destination->AddAuthority(Moving,Error)) return false;
    if(Quantity==Contents.Items[Index].Quantity) { Contents.Items.RemoveAt(Index); Contents.MarkArrayDirty(); }
    else { Contents.Items[Index].Quantity-=Quantity; Contents.MarkItemDirty(Contents.Items[Index]); }
    GetOwner()->ForceNetUpdate(); return true;
}
bool URVInventoryComponent::ConsumeOneAuthority(const FGuid& Id, FRVItemInstance& Consumed, FString& Error)
{
    if (!GetOwner() || !GetOwner()->HasAuthority()) { Error=TEXT("Authority required"); return false; }
    const int32 Index=Contents.Items.IndexOfByPredicate([&](const auto& I){return I.Id==Id;});
    if(Index==INDEX_NONE || Contents.Items[Index].Quantity<1) { Error=TEXT("Item no longer owned"); return false; }
    if(Contents.Items[Index].LoadedInWeapon.IsValid() || (Contents.Items[Index].Definition &&
       (Contents.Items[Index].Definition->Combat.bFirearm || Contents.Items[Index].Definition->Combat.bMagazine)))
    {Error=TEXT("Combat items cannot be consumed");return false;}
    Consumed=Contents.Items[Index]; Consumed.Quantity=1;
    if(Contents.Items[Index].Quantity==1) { Contents.Items.RemoveAt(Index); Contents.MarkArrayDirty(); }
    else { --Contents.Items[Index].Quantity; Contents.MarkItemDirty(Contents.Items[Index]); }
    GetOwner()->ForceNetUpdate(); return true;
}
bool URVInventoryComponent::SwapMagazineAuthority(FGuid Weapon,FGuid Magazine,int32 Revision,FString& Error)
{
    if(!GetOwner() || !GetOwner()->HasAuthority()){Error=TEXT("Authority required");return false;}
    auto* W=Contents.Items.FindByPredicate([&](const auto& I){return I.Id==Weapon;});
    auto* M=Contents.Items.FindByPredicate([&](const auto& I){return I.Id==Magazine;});
    if(!W || !W->Definition || !W->Definition->Combat.bFirearm || W->CombatRevision!=Revision)
    {Error=TEXT("Stale or unowned weapon");return false;}
    if(!M || !M->Definition || !M->Definition->Combat.bMagazine || M->LoadedInWeapon.IsValid()
        || !M->bMagazineInitialized || M->Definition->Combat.Caliber!=W->Definition->Combat.Caliber || M->Condition<=0)
    {Error=TEXT("Compatible spare magazine required");return false;}
    for(auto& I:Contents.Items)if(I.LoadedInWeapon==Weapon)
    {I.LoadedInWeapon.Invalidate();++I.CombatRevision;Contents.MarkItemDirty(I);}
    M->LoadedInWeapon=Weapon;++M->CombatRevision;++W->CombatRevision;
    Contents.MarkItemDirty(*M);Contents.MarkItemDirty(*W);GetOwner()->ForceNetUpdate();Error.Empty();return true;
}
bool URVInventoryComponent::ReleaseMagazineAuthority(FGuid Weapon)
{
    if(!GetOwner() || !GetOwner()->HasAuthority() || !Weapon.IsValid())return false;
    bool Changed=false;
    for(auto& I:Contents.Items)if(I.LoadedInWeapon==Weapon)
    {I.LoadedInWeapon.Invalidate();++I.CombatRevision;Contents.MarkItemDirty(I);Changed=true;}
    if(Changed)if(auto* W=Contents.Items.FindByPredicate([&](const auto& I){return I.Id==Weapon;}))
    {++W->CombatRevision;Contents.MarkItemDirty(*W);}
    if(Changed)GetOwner()->ForceNetUpdate();return Changed;
}
bool URVInventoryComponent::FireMagazineAuthority(FGuid Weapon,int32 Revision,FRVItemInstance& FiredWeapon,FString& Error)
{
    if(!GetOwner() || !GetOwner()->HasAuthority()){Error=TEXT("Authority required");return false;}
    auto* W=Contents.Items.FindByPredicate([&](const auto& I){return I.Id==Weapon;});
    auto* M=Contents.Items.FindByPredicate([&](const auto& I){return I.LoadedInWeapon==Weapon;});
    if(!W || !W->Definition || !W->Definition->Combat.bFirearm || W->CombatRevision!=Revision || W->Condition<=0)
    {Error=TEXT("Stale or unowned weapon");return false;}
    if(!M || !M->Definition || !M->bMagazineInitialized || M->MagazineRounds<=0)
    {Error=TEXT("Magazine empty — reload");return false;}
    --M->MagazineRounds;++M->CombatRevision;++W->CombatRevision;
    FiredWeapon=*W;Contents.MarkItemDirty(*M);Contents.MarkItemDirty(*W);GetOwner()->ForceNetUpdate();Error.Empty();return true;
}
void URVInventoryComponent::OpenContainerAuthority(URVInventoryComponent* Container)
{ if(GetOwner()->HasAuthority()) { OpenContainer=Container; Feedback.Empty(); GetOwner()->ForceNetUpdate(); } }
void URVInventoryComponent::RequestTransfer(FGuid Id, int32 Quantity, bool bToContainer)
{
    const auto* Pawn=Cast<APawn>(GetOwner());
    if(!Pawn || !Pawn->IsLocallyControlled()) return;
    // Dispatch in the native world tick. Weak delegates do not keep pawns/worlds alive.
    // This also avoids editor script guards forcing network functions to execute locally.
    GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Id,Quantity,bToContainer]
    { const auto* P=Cast<APawn>(GetOwner()); if(P && P->IsLocallyControlled()) ServerTransfer(Id,Quantity,bToContainer); }));
}
void URVInventoryComponent::RequestDrop(FGuid Id, int32 Quantity)
{
    const auto* Pawn=Cast<APawn>(GetOwner()); if(!Pawn || !Pawn->IsLocallyControlled()) return;
    GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this,Id,Quantity]
    { const auto* P=Cast<APawn>(GetOwner()); if(P && P->IsLocallyControlled()) ServerDrop(Id,Quantity); }));
}
void URVInventoryComponent::RequestCloseContainer()
{
    const auto* Pawn=Cast<APawn>(GetOwner()); if(!Pawn || !Pawn->IsLocallyControlled()) return;
    GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateWeakLambda(this,[this]
    { const auto* P=Cast<APawn>(GetOwner()); if(P && P->IsLocallyControlled()) ServerCloseContainer(); }));
}
void URVInventoryComponent::ServerCloseContainer_Implementation()
{ if(!GetOwner()->HasAuthority()) return; OpenContainer=nullptr; Feedback.Empty(); GetOwner()->ForceNetUpdate(); }
void URVInventoryComponent::ServerTransfer_Implementation(FGuid Id, int32 Quantity, bool bToContainer)
{
    if(!GetOwner()->HasAuthority()) return;
    if(const auto* P=Cast<APawn>(GetOwner())) if(const auto* PS=P->GetPlayerState<ARVPlayerState>();PS && !PS->Health->CanAct()) { Feedback=TEXT("Cannot transfer while downed");return; }
    if(InventoryDebug.GetValueOnGameThread()) UE_LOG(LogRVNetworking,Log,TEXT("Inventory transfer role=%d owner=%s item=%s quantity=%d"),int32(GetOwner()->GetLocalRole()),*GetOwner()->GetName(),*Id.ToString(),Quantity);
    const APawn* Pawn=Cast<APawn>(GetOwner());
    if(!Pawn || !Pawn->GetController() || !IsValid(OpenContainer) || !IsValid(OpenContainer->GetOwner())) return;
    FVector Eye; FRotator Rotation; Pawn->GetActorEyesViewPoint(Eye,Rotation);
    const FVector Target=OpenContainer->GetOwner()->GetActorLocation();
    FHitResult Hit; FCollisionQueryParams Params(SCENE_QUERY_STAT(RVStorageAccess),false,Pawn);
    if(FVector::DistSquared(Eye,Target)>FMath::Square(300.f) ||
       (GetWorld()->LineTraceSingleByChannel(Hit,Eye,Target,ECC_Visibility,Params) && Hit.GetActor()!=OpenContainer->GetOwner()))
    { Feedback=TEXT("Container out of reach or obstructed"); OpenContainer=nullptr; return; }
    auto* Source=bToContainer?this:OpenContainer.Get(); auto* Destination=bToContainer?OpenContainer.Get():this;
    Source->TransferAuthority(Destination,Id,Quantity,Feedback); GetOwner()->ForceNetUpdate();
}
void URVInventoryComponent::ServerDrop_Implementation(FGuid Id, int32 Quantity)
{
    if(!GetOwner()->HasAuthority()) return;
    if(const auto* P=Cast<APawn>(GetOwner())) if(const auto* PS=P->GetPlayerState<ARVPlayerState>();PS && !PS->Health->CanAct()) { Feedback=TEXT("Cannot drop while downed");return; }
    const APawn* Pawn=Cast<APawn>(GetOwner()); if(!Pawn || !Pawn->GetController()) return;
    const int32 Index=Contents.Items.IndexOfByPredicate([&](const auto& I){return I.Id==Id;});
    if(Index==INDEX_NONE || Quantity<=0 || Quantity>Contents.Items[Index].Quantity) return;
    if(Contents.Items[Index].LoadedInWeapon.IsValid() || Contents.Items.ContainsByPredicate([&](const auto& I){return I.LoadedInWeapon==Id;}))
    {Feedback=TEXT("Unload weapon before dropping");return;}
    FVector Eye; FRotator Rotation; Pawn->GetActorEyesViewPoint(Eye,Rotation);
    FCollisionQueryParams Params(SCENE_QUERY_STAT(RVDrop),false,Pawn);
    FHitResult Hit; FVector Position; bool bFound=false; UPrimitiveComponent* Support=nullptr;
    const auto* Character=Cast<ACharacter>(Pawn);
    const float FeetZ=Pawn->GetActorLocation().Z-(Character?Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight():0.f);
    for(float Offset:{0.f,45.f,-45.f,90.f,-90.f})
    {
        const FVector Candidate=Eye+FRotator(0,Rotation.Yaw+Offset,0).Vector()*100;
        if(GetWorld()->SweepSingleByChannel(Hit,Eye,Candidate,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(20),Params))
        { if(InventoryDebug.GetValueOnGameThread()) UE_LOG(LogRVNetworking,Log,TEXT("Drop offset=%.0f path blocked by %s"),Offset,*GetNameSafe(Hit.GetComponent())); continue; }
        // Use the same query collision as interior interaction and safe vehicle exits.
        // WorldStatic hits the RV's coarse physics chassis above its walkable cabin floor.
        if(!GetWorld()->LineTraceSingleByChannel(Hit,Candidate,Candidate-FVector(0,0,220),ECC_Visibility,Params) || Hit.Normal.Z<.7)
        { if(InventoryDebug.GetValueOnGameThread()) UE_LOG(LogRVNetworking,Log,TEXT("Drop offset=%.0f no suitable support %s normal=%.2f"),Offset,*GetNameSafe(Hit.GetComponent()),Hit.Normal.Z); continue; }
        if(Hit.Location.Z<FeetZ-45 || Hit.Location.Z>FeetZ+60)
        { if(InventoryDebug.GetValueOnGameThread()) UE_LOG(LogRVNetworking,Log,TEXT("Drop offset=%.0f support %s height delta=%.2f"),Offset,*GetNameSafe(Hit.GetComponent()),Hit.Location.Z-FeetZ); continue; }
        Position=Hit.Location+FVector(0,0,20);
        if(GetWorld()->OverlapBlockingTestByChannel(Position,FQuat::Identity,ECC_Visibility,FCollisionShape::MakeSphere(18),Params))
        { if(InventoryDebug.GetValueOnGameThread()) UE_LOG(LogRVNetworking,Log,TEXT("Drop offset=%.0f landing overlap at %s"),Offset,*Position.ToString()); continue; }
        Support=Hit.GetComponent();
        bFound=true; break;
    }
    if(!bFound) { Feedback=TEXT("No safe drop location"); return; }
    FTransform Transform(FRotator::ZeroRotator,Position);
    auto* Pickup=GetWorld()->SpawnActorDeferred<ARVWorldItem>(ARVWorldItem::StaticClass(),Transform);
    if(!Pickup) { Feedback=TEXT("Drop failed"); return; }
    Pickup->Item=Contents.Items[Index]; Pickup->Item.Quantity=Quantity;
    if(Quantity<Contents.Items[Index].Quantity) Pickup->Item.Id=FGuid::NewGuid();
    Pickup->FinishSpawning(Transform);
    if(Support && Support->ComponentHasTag(TEXT("RVPassengerPlatform")))
        Pickup->AttachToComponent(Support,FAttachmentTransformRules::KeepWorldTransform);
    if(Quantity==Contents.Items[Index].Quantity) { Contents.Items.RemoveAt(Index); Contents.MarkArrayDirty(); }
    else { Contents.Items[Index].Quantity-=Quantity; Contents.MarkItemDirty(Contents.Items[Index]); }
    Feedback.Empty(); GetOwner()->ForceNetUpdate();
}



bool URVInventoryComponent::RefuelAuthority(URVFuelComponent* Tank, const FGuid& Id, int32 Revision, double& Transferred, FString& Error)
{
    Transferred=0;
    if(!GetOwner() || !GetOwner()->HasAuthority() || !Tank || !Tank->GetOwner()->HasAuthority())
    { Error=TEXT("Authority required"); return false; }
    auto* I=Contents.Items.FindByPredicate([&](const auto& Item){return Item.Id==Id;});
    if(!I || !I->Definition || !I->Definition->Fuel.bFuelContainer || !I->bFuelInitialized || I->Quantity!=1)
    { Error=TEXT("Fuel can not owned"); return false; }
    if(Revision!=I->FuelRevision) { Error=TEXT("Stale fuel can request"); return false; }
    if(I->Definition->Fuel.FuelType!=Tank->FuelType) { Error=TEXT("Incompatible fuel"); return false; }
    if(!FMath::IsFinite(I->FuelLitres) || I->FuelLitres<=0) { Error=TEXT("Fuel can empty"); return false; }
    Transferred=Tank->AddAuthority(I->FuelLitres);
    if(Transferred<=0) { Error=TEXT("Tank full"); return false; }
    I->FuelLitres=FMath::Max(0.,I->FuelLitres-Transferred); ++I->FuelRevision;
    Contents.MarkItemDirty(*I); GetOwner()->ForceNetUpdate(); Error.Empty(); return true;
}
bool URVInventoryComponent::DebugSetFuelCan(FGuid Id, double Litres)
{
#if !UE_BUILD_SHIPPING
    if(!GetOwner() || !GetOwner()->HasAuthority() || !URVFuelComponent::DebugAllowed() || !FMath::IsFinite(Litres)) return false;
    auto* I=Contents.Items.FindByPredicate([&](const auto& Item){return Item.Id==Id;});
    if(!I || !I->Definition || !I->Definition->Fuel.bFuelContainer) return false;
    I->bFuelInitialized=true; I->FuelLitres=FMath::Clamp(Litres,0.,I->Definition->Fuel.CapacityLitres); ++I->FuelRevision;
    Contents.MarkItemDirty(*I); GetOwner()->ForceNetUpdate(); return true;
#else
    return false;
#endif
}

bool URVInventoryComponent::DrainFluidAuthority(const FGuid& Id,int32 Revision,FGameplayTag Type,double Maximum,double& Drained,FString& Error)
{
    Drained=0;
    if(!GetOwner() || !GetOwner()->HasAuthority() || !Type.IsValid() || !FMath::IsFinite(Maximum) || Maximum<=0)
    {Error=TEXT("Invalid fluid transfer");return false;}
    auto* I=Contents.Items.FindByPredicate([&](const auto& Item){return Item.Id==Id;});
    if(!I || !I->Definition || !I->Definition->Fuel.bFuelContainer || !I->bFuelInitialized || I->Quantity!=1 || I->Definition->Fuel.FuelType!=Type)
    {Error=TEXT("Compatible fluid container not owned");return false;}
    if(Revision!=I->FuelRevision){Error=TEXT("Stale fluid request");return false;}
    if(!FMath::IsFinite(I->FuelLitres) || I->FuelLitres<=0 || I->FuelLitres>I->Definition->Fuel.CapacityLitres)
    {Error=TEXT("Fluid container empty or invalid");return false;}
    Drained=FMath::Min(Maximum,I->FuelLitres);I->FuelLitres-=Drained;++I->FuelRevision;
    Contents.MarkItemDirty(*I);GetOwner()->ForceNetUpdate();Error.Empty();return true;
}
bool URVInventoryComponent::RepairRequirementsAuthority(const TArray<FRVRepairRequirement>& Requirements,bool Commit,FString& Error)
{
    if(!GetOwner() || !GetOwner()->HasAuthority() || Requirements.IsEmpty()){Error=TEXT("Invalid repair requirements");return false;}
    TArray<int32> Consume;Consume.Init(0,Contents.Items.Num());
    for(const auto& R:Requirements)
    {
        if(!R.Tag.IsValid() || R.Quantity<=0 || R.Quantity>1000 || !FMath::IsFinite(R.MinimumCondition) || R.MinimumCondition<0 || R.MinimumCondition>1)
        {Error=TEXT("Invalid repair configuration");return false;}
        int32 Need=R.Quantity;
        for(int32 N=0;N<Contents.Items.Num() && Need>0;++N)
        {
            const auto& I=Contents.Items[N];
            if(!I.Definition || I.Condition<R.MinimumCondition || !I.Definition->Tags.HasTag(R.Tag))continue;
            const int32 Taken=FMath::Min(Need,FMath::Max(0,I.Quantity-Consume[N]));Need-=Taken;
            if(R.bConsume)Consume[N]+=Taken;
        }
        if(Need>0){Error=FString::Printf(TEXT("Missing usable %s x%d"),R.DisplayName.IsEmpty()?TEXT("repair supplies"):*R.DisplayName.ToString(),Need);return false;}
    }
    if(Commit)
    {
        // Validate every requirement before any mutation; no yield or callback
        // between the inventory commit and the service outcome on the game thread.
        for(int32 N=Contents.Items.Num()-1;N>=0;--N)if(Consume[N]>0)
        {
            Contents.Items[N].Quantity-=Consume[N];
            if(Contents.Items[N].Quantity<=0){Contents.Items.RemoveAt(N);Contents.MarkArrayDirty();}
            else Contents.MarkItemDirty(Contents.Items[N]);
        }
        GetOwner()->ForceNetUpdate();
    }
    Error.Empty();return true;
}
