#include "Player/RVCharacterContentLibrary.h"
#include "Player/RVHumanoidAnimInstance.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimBlueprint.h"
#include "Animation/BlendSpace.h"
#include "Animation/Skeleton.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/SkeletalMeshActor.h"
#include "Engine/World.h"
#include "Camera/CameraActor.h"
AActor* URVCharacterContentLibrary::SpawnObservationCamera(UObject* Context,FVector Position,FRotator Rotation)
{
#if WITH_EDITOR
    UWorld* World=Context?Context->GetWorld():nullptr;
    if(!World || !World->IsGameWorld()) return nullptr;
    FActorSpawnParameters Params;Params.ObjectFlags|=RF_Transient;
    Params.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    auto* Camera=World->SpawnActor<ACameraActor>(Position,Rotation,Params);
    if(Camera) if(auto* Parent=Cast<AActor>(Context)) Camera->AttachToActor(Parent,FAttachmentTransformRules::KeepWorldTransform);
    return Camera;
#else
    return nullptr;
#endif
}
AActor* URVCharacterContentLibrary::SpawnPoseFixture(UObject* Context,FVector Position)
{
#if WITH_EDITOR
    UWorld* World=Context?Context->GetWorld():nullptr;
    if(!World || !World->IsGameWorld()) return nullptr;
    FActorSpawnParameters Params;Params.ObjectFlags|=RF_Transient;
    Params.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    return World->SpawnActor<ASkeletalMeshActor>(Position,FRotator::ZeroRotator,Params);
#else
    return nullptr;
#endif
}
#if WITH_EDITOR
#include "Animation/AnimData/IAnimationDataController.h"
#include "Animation/AnimData/IAnimationDataModel.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "AnimGraphNode_Root.h"
#include "AnimGraphNode_TwoBoneIK.h"
#include "AnimGraphNode_ModifyBone.h"
#include "AnimGraphNode_LocalToComponentSpace.h"
#include "AnimGraphNode_ComponentToLocalSpace.h"
#include "AnimGraphNode_BlendListByInt.h"
#include "AnimGraphNode_BlendSpacePlayer.h"
#include "AnimGraphNode_SequencePlayer.h"
#include "K2Node_VariableGet.h"
#include "AnimGraphNode_BlendListByBool.h"
#include "AnimGraphNode_LayeredBoneBlend.h"
#include "AnimGraphNode_CopyPoseFromMesh.h"
#include "AnimGraphNode_CopyBone.h"
#include "AnimGraphNode_Slot.h"
#include "AnimGraphNode_RotationOffsetBlendSpace.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphSchema.h"
#include "EdGraph/EdGraphNodeUtils.h"
#include "Misc/PackageName.h"
#include "UObject/UnrealType.h"
#endif
TMap<FName,FTransform> URVCharacterContentLibrary::GetPoseBoneTransforms(UAnimSequence* Pose,USkeletalMesh* Mesh)
{
    TMap<FName,FTransform> Result;
#if WITH_EDITOR
    if(!Pose || !Mesh || Pose->GetSkeleton()!=Mesh->GetSkeleton()) return Result;
    const auto& Ref=Mesh->GetRefSkeleton();TArray<FTransform> Global;Global.SetNum(Ref.GetNum());
    for(int32 Bone=0;Bone<Ref.GetNum();++Bone)
    {
        const FName Name=Ref.GetBoneName(Bone);
        FTransform Local=Ref.GetRefBonePose()[Bone];
        if(Pose->GetDataModel()->IsValidBoneTrackName(Name)) Local=Pose->GetDataModel()->GetBoneTrackTransform(Name,FFrameNumber(0));
        const int32 Parent=Ref.GetParentIndex(Bone);
        Global[Bone]=Parent==INDEX_NONE?Local:Local*Global[Parent];Result.Add(Name,Global[Bone]);
    }
#endif
    return Result;
}
bool URVCharacterContentLibrary::AlignPoseBones(UAnimSequence* Pose,USkeletalMesh* Mesh,const TMap<FName,FVector>& Directions)
{
#if WITH_EDITOR
    if(!Pose || !Mesh || Pose->GetSkeleton()!=Mesh->GetSkeleton() || !Pose->GetPathName().StartsWith(TEXT("/Game/Characters/RV/"))) return false;
    const auto& Ref=Mesh->GetRefSkeleton();TArray<FTransform> Local;TArray<FQuat> Global;
    Local.SetNum(Ref.GetNum());Global.SetNum(Ref.GetNum());
    for(int32 Bone=0;Bone<Ref.GetNum();++Bone)
    {
        const int32 Index=Mesh->GetSkeleton()->GetReferenceSkeleton().FindBoneIndex(Ref.GetBoneName(Bone));
        Local[Bone]=Ref.GetRefBonePose()[Bone];
        if(Index!=INDEX_NONE && Pose->GetDataModel()->IsValidBoneTrackName(Ref.GetBoneName(Bone))) Local[Bone]=Pose->GetDataModel()->GetBoneTrackTransform(Ref.GetBoneName(Bone),FFrameNumber(0));
    }
    auto& Controller=Pose->GetController();Controller.OpenBracket(FText::FromString(TEXT("Align prototype pose limbs")),false);
    for(int32 Bone=0;Bone<Ref.GetNum();++Bone)
    {
        const int32 Parent=Ref.GetParentIndex(Bone);const FQuat ParentRotation=Parent==INDEX_NONE?FQuat::Identity:Global[Parent];
        Global[Bone]=ParentRotation*Local[Bone].GetRotation();
        if(const auto* Direction=Directions.Find(Ref.GetBoneName(Bone)))
        {
            FVector ChildVector=FVector::ZeroVector;
            for(int32 Child=Bone+1;Child<Ref.GetNum();++Child)
                if(Ref.GetParentIndex(Child)==Bone && Local[Child].GetTranslation().SizeSquared()>ChildVector.SizeSquared()) ChildVector=Local[Child].GetTranslation();
            if(!ChildVector.IsNearlyZero() && !Direction->IsNearlyZero())
            {
                Global[Bone]=FQuat::FindBetweenNormals(Global[Bone].RotateVector(ChildVector).GetSafeNormal(),Direction->GetSafeNormal())*Global[Bone];
                Local[Bone].SetRotation(ParentRotation.Inverse()*Global[Bone]);
                TArray<FVector> Positions,Scales;TArray<FQuat> Rotations;
                for(int32 Frame=0;Frame<=30;++Frame){Positions.Add(Local[Bone].GetTranslation());Scales.Add(Local[Bone].GetScale3D());Rotations.Add(Local[Bone].GetRotation());}
                Controller.SetBoneTrackKeys(Ref.GetBoneName(Bone),Positions,Rotations,Scales,false);
            }
        }
    }
    Controller.NotifyPopulated();Controller.CloseBracket(false);Pose->PostEditChange();
    Pose->CacheDerivedDataForCurrentPlatform();Pose->WaitOnExistingCompression();
    Pose->MarkPackageDirty();return true;
#else
    return false;
#endif
}
UAnimSequence* URVCharacterContentLibrary::CreatePrototypePose(const FString& AssetPath,USkeletalMesh* Mesh,const TMap<FName,FRotator>& BoneRotations,bool Climbing,UAnimSequence* BasePose)
{
#if WITH_EDITOR
    if(!Mesh || !AssetPath.StartsWith(TEXT("/Game/Characters/RV/"))) return nullptr;
    auto* Sequence=LoadObject<UAnimSequence>(nullptr,*AssetPath);const bool Created=!Sequence;
    if(Created) Sequence=NewObject<UAnimSequence>(CreatePackage(*AssetPath),*FPackageName::GetLongPackageAssetName(AssetPath),RF_Public|RF_Standalone|RF_Transactional);
    Sequence->SetSkeleton(Mesh->GetSkeleton());Sequence->SetPreviewMesh(Mesh);Sequence->bEnableRootMotion=false;
    auto& Controller=Sequence->GetController();if(Created) Controller.InitializeModel();Controller.OpenBracket(FText::FromString(TEXT("Author prototype visual pose")),false);
    Controller.SetFrameRate(FFrameRate(30,1),false);Controller.SetNumberOfFrames(FFrameNumber(30),false);
    const auto& Skeleton=Mesh->GetRefSkeleton();
    for(int32 Bone=0;Bone<Skeleton.GetNum();++Bone)
    {
        const FName Name=Skeleton.GetBoneName(Bone);FTransform Reference=Skeleton.GetRefBonePose()[Bone];
        if(BasePose && BasePose->GetSkeleton()==Mesh->GetSkeleton())
        {
            const int32 Index=Mesh->GetSkeleton()->GetReferenceSkeleton().FindBoneIndex(Name);
            if(Index!=INDEX_NONE) BasePose->GetBoneTransform(Reference,FSkeletonPoseBoneIndex(Index),FAnimExtractContext(0,false),true);
        }
        TArray<FVector> Positions,Scales;TArray<FQuat> Rotations;
        for(int32 Frame=0;Frame<=30;++Frame)
        {
            FQuat Rotation=Reference.GetRotation();
            if(const auto* Offset=BoneRotations.Find(Name)) Rotation=Rotation*Offset->Quaternion();
            if(Climbing && (Name==TEXT("thigh_l") || Name==TEXT("thigh_r") || Name==TEXT("calf_l") || Name==TEXT("calf_r")))
            {
                const float Phase=Name.ToString().EndsWith(TEXT("_l"))?0.f:PI;
                Rotation=Rotation*FRotator(0,0,FMath::Sin(Frame/30.f*2*PI+Phase)*18).Quaternion();
            }
            Positions.Add(Reference.GetLocation());Rotations.Add(Rotation);Scales.Add(Reference.GetScale3D());
        }
        if(Created) Controller.AddBoneCurve(Name,false);Controller.SetBoneTrackKeys(Name,Positions,Rotations,Scales,false);
    }
    Controller.NotifyPopulated();Controller.CloseBracket(false);Sequence->PostEditChange();Sequence->MarkPackageDirty();if(Created) FAssetRegistryModule::AssetCreated(Sequence);return Sequence;
#else
    return nullptr;
#endif
}
UAnimSequence* URVCharacterContentLibrary::CreatePrototypeMelee(const FString& Path,USkeletalMesh* Mesh,bool Shove,UAnimSequence* BasePose)
{
#if WITH_EDITOR
    UAnimSequence* Sequence=CreatePrototypePose(Path,Mesh,{},false,BasePose);if(!Sequence)return nullptr;
    auto& Controller=Sequence->GetController();Controller.OpenBracket(FText::FromString(TEXT("Prototype melee visual swing")),false);
    for(FName Name:{FName(TEXT("upperarm_r")),FName(TEXT("lowerarm_r")),FName(TEXT("upperarm_l")),FName(TEXT("lowerarm_l")),FName(TEXT("spine_03"))})
    {
        if(!Sequence->GetDataModel()->IsValidBoneTrackName(Name))continue;
        const FTransform Base=Sequence->GetDataModel()->GetBoneTrackTransform(Name,FFrameNumber(0));
        TArray<FVector> Locations,Scales;TArray<FQuat> Rotations;
        for(int32 Frame=0;Frame<=30;++Frame)
        {
            const float Phase=Frame/30.f,Envelope=FMath::Sin(Phase*PI);
            const bool Left=Name.ToString().EndsWith(TEXT("_l"));const bool Lower=Name.ToString().StartsWith(TEXT("lower"));
            FRotator Offset=FRotator::ZeroRotator;
            if(Name==TEXT("spine_03"))Offset.Yaw=(Shove?8.f:25.f)*Envelope;
            else if(Shove)Offset=FRotator((Lower?-35.f:65.f)*Envelope,(Left?-10.f:10.f)*Envelope,0);
            else if(!Left)Offset=FRotator((Lower?-45.f:100.f)*Envelope,45.f*FMath::Sin(Phase*2*PI),-25.f*Envelope);
            Locations.Add(Base.GetLocation());Scales.Add(Base.GetScale3D());Rotations.Add(Base.GetRotation()*Offset.Quaternion());
        }
        Controller.SetBoneTrackKeys(Name,Locations,Rotations,Scales,false);
    }
    Controller.NotifyPopulated();Controller.CloseBracket(false);Sequence->PostEditChange();Sequence->MarkPackageDirty();return Sequence;
#else
    return nullptr;
#endif
}
bool URVCharacterContentLibrary::PopulateLocomotion(UBlendSpace* BlendSpace,const TArray<UAnimSequence*>& Clips,const TArray<FVector>& Coordinates)
{
#if WITH_EDITOR
    if(!BlendSpace || Clips.Num()!=Coordinates.Num() || Clips.IsEmpty()) return false;
    auto* Property=FindFProperty<FStructProperty>(UBlendSpace::StaticClass(),TEXT("BlendParameters"));if(!Property) return false;
    auto* Speed=Property->ContainerPtrToValuePtr<FBlendParameter>(BlendSpace,0);auto* Direction=Property->ContainerPtrToValuePtr<FBlendParameter>(BlendSpace,1);
    Speed->DisplayName=TEXT("Ground speed");Speed->Min=0;Speed->Max=600;Speed->GridNum=4;
    Direction->DisplayName=TEXT("Direction");Direction->Min=-180;Direction->Max=180;Direction->GridNum=8;
    while(BlendSpace->GetNumberOfBlendSamples()>0) BlendSpace->DeleteSample(0);
    for(int32 Index=0;Index<Clips.Num();++Index) if(!Clips[Index] || BlendSpace->AddSample(Clips[Index],Coordinates[Index])==INDEX_NONE) return false;
    BlendSpace->ValidateSampleData();BlendSpace->ResampleData();BlendSpace->PostEditChange();BlendSpace->MarkPackageDirty();return true;
#else
    return false;
#endif
}
bool URVCharacterContentLibrary::BuildAnimationGraph(UAnimBlueprint* Blueprint,UBlendSpace* Locomotion,const TArray<UAnimSequence*>& Poses,UBlendSpace* ArmedLocomotion,UBlendSpace* WeaponAimOffset,UAnimSequence* OneHandReady)
{
#if WITH_EDITOR
    if(!Blueprint || !Locomotion || Poses.Num()!=10 || !Blueprint->ParentClass->IsChildOf(URVHumanoidAnimInstance::StaticClass())) return false;
    UEdGraph* Graph=nullptr;for(auto Candidate:Blueprint->FunctionGraphs) if(Candidate->GetFName()==TEXT("AnimGraph")) Graph=Candidate.Get();
    if(!Graph) return false;
    UAnimGraphNode_Root* Root=nullptr;
    const auto OldNodes=Graph->Nodes;
    for(auto Node:OldNodes) if(auto* Candidate=Cast<UAnimGraphNode_Root>(Node.Get())) Root=Candidate;else Graph->RemoveNode(Node.Get());
    if(!Root) return false;
    const auto* Schema=Graph->GetSchema();bool Success=true;
    auto Link=[&](UEdGraphNode* From,FName Output,UEdGraphNode* To,FName Input)
    {auto* A=From->FindPin(Output);auto* B=To->FindPin(Input);Success=Success && A && B && Schema->TryCreateConnection(A,B);};
    auto Variable=[&](FName Name,int32 Y)
    {FGraphNodeCreator<UK2Node_VariableGet> Create(*Graph);auto* Node=Create.CreateNode();Node->VariableReference.SetSelfMember(Name);Node->NodePosX=-900;Node->NodePosY=Y;Create.Finalize();return Node;};
    FGraphNodeCreator<UAnimGraphNode_BlendSpacePlayer> MakeWalk(*Graph);auto* Walk=MakeWalk.CreateNode();MakeWalk.Finalize();Walk->SetAnimationAsset(Locomotion);Walk->NodePosX=-600;Walk->ReconstructNode();
    Link(Variable(TEXT("GroundSpeed"),0),TEXT("GroundSpeed"),Walk,TEXT("X"));Link(Variable(TEXT("Direction"),100),TEXT("Direction"),Walk,TEXT("Y"));
    FGraphNodeCreator<UAnimGraphNode_BlendListByInt> MakeModes(*Graph);auto* Modes=MakeModes.CreateNode();MakeModes.Finalize();
    while(Modes->Node.GetBlendTimes().Num()<11) Modes->Node.AddPose();Modes->ReconstructNode();Modes->NodePosX=0;
    Link(Variable(TEXT("PoseIndex"),-200),TEXT("PoseIndex"),Modes,TEXT("ActiveChildIndex"));
    if(ArmedLocomotion)
    {
        FGraphNodeCreator<UAnimGraphNode_BlendSpacePlayer> MakeArmed(*Graph);auto* Armed=MakeArmed.CreateNode();MakeArmed.Finalize();Armed->SetAnimationAsset(ArmedLocomotion);Armed->ReconstructNode();Armed->NodePosX=-600;Armed->NodePosY=-300;
        if(OneHandReady)
        {for(auto& P:Armed->ShowPinForProperties)if(P.PropertyName==TEXT("BlendSpace"))P.bShowPin=true;
         Armed->ReconstructNode();Link(Variable(TEXT("WeaponLocomotion"),-1000),TEXT("WeaponLocomotion"),Armed,TEXT("BlendSpace"));}
        Link(Variable(TEXT("GroundSpeed"),-450),TEXT("GroundSpeed"),Armed,TEXT("X"));Link(Variable(TEXT("Direction"),-350),TEXT("Direction"),Armed,TEXT("Y"));
        FGraphNodeCreator<UAnimGraphNode_BlendListByBool> MakeReady(*Graph);auto* Ready=MakeReady.CreateNode();MakeReady.Finalize();Ready->ReconstructNode();
        Link(Walk,TEXT("Pose"),Ready,TEXT("BlendPose_1"));
        if(WeaponAimOffset)
        {FGraphNodeCreator<UAnimGraphNode_RotationOffsetBlendSpace> MakeAim(*Graph);auto* Aim=MakeAim.CreateNode();MakeAim.Finalize();Aim->SetAnimationAsset(WeaponAimOffset);Aim->ReconstructNode();
         if(OneHandReady){for(auto& P:Aim->ShowPinForProperties)if(P.PropertyName==TEXT("BlendSpace"))P.bShowPin=true;
          Aim->ReconstructNode();Link(Variable(TEXT("WeaponAim"),-1100),TEXT("WeaponAim"),Aim,TEXT("BlendSpace"));}
         Link(Armed,TEXT("Pose"),Aim,TEXT("BasePose"));Link(Variable(TEXT("NormalizedAimPitch"),-650),TEXT("NormalizedAimPitch"),Aim,TEXT("Y"));Link(Aim,TEXT("Pose"),Ready,TEXT("BlendPose_0"));}
        else Link(Armed,TEXT("Pose"),Ready,TEXT("BlendPose_0"));
        Link(Variable(TEXT("bWeaponReady"),-550),TEXT("bWeaponReady"),Ready,TEXT("bActiveValue"));
        if(OneHandReady)
        {
            FGraphNodeCreator<UAnimGraphNode_SequencePlayer> MakeTool(*Graph);auto* Tool=MakeTool.CreateNode();MakeTool.Finalize();Tool->SetAnimationAsset(OneHandReady);Tool->ReconstructNode();
            for(auto& P:Tool->ShowPinForProperties)if(P.PropertyName==TEXT("Sequence"))P.bShowPin=true;
            Tool->ReconstructNode();Link(Variable(TEXT("WeaponReadyPose"),-1200),TEXT("WeaponReadyPose"),Tool,TEXT("Sequence"));
            FGraphNodeCreator<UAnimGraphNode_LayeredBoneBlend> MakeOverlay(*Graph);auto* Overlay=MakeOverlay.CreateNode();Overlay->Node.AddPose();
            Overlay->Node.LayerSetup[0].BranchFilters.Add(FBranchFilter(TEXT("spine_01"),3));Overlay->Node.bMeshSpaceRotationBlend=true;
            MakeOverlay.Finalize();Overlay->ReconstructNode();
            Link(Walk,TEXT("Pose"),Overlay,TEXT("BasePose"));Link(Tool,TEXT("Pose"),Overlay,TEXT("BlendPoses_0"));
            FGraphNodeCreator<UAnimGraphNode_BlendListByBool> MakeFamily(*Graph);auto* Family=MakeFamily.CreateNode();MakeFamily.Finalize();Family->ReconstructNode();
            Link(Overlay,TEXT("Pose"),Family,TEXT("BlendPose_0"));Link(Ready,TEXT("Pose"),Family,TEXT("BlendPose_1"));
            Link(Variable(TEXT("bOneHandedMelee"),-800),TEXT("bOneHandedMelee"),Family,TEXT("bActiveValue"));
            Link(Family,TEXT("Pose"),Modes,TEXT("BlendPose_0"));
        }
        else Link(Ready,TEXT("Pose"),Modes,TEXT("BlendPose_0"));
    }
    else Link(Walk,TEXT("Pose"),Modes,TEXT("BlendPose_0"));
    for(int32 Index=0;Index<Poses.Num();++Index)
    {
        FGraphNodeCreator<UAnimGraphNode_SequencePlayer> MakePose(*Graph);auto* Player=MakePose.CreateNode();MakePose.Finalize();Player->SetAnimationAsset(Poses[Index]);Player->NodePosX=-600;Player->NodePosY=(Index+1)*180;
        if(Index==4)
        {
            for(auto& Optional:Player->ShowPinForProperties) if(Optional.PropertyName==TEXT("PlayRate")) Optional.bShowPin=true;
            Player->ReconstructNode();Link(Variable(TEXT("ClimbPlayRate"),800),TEXT("ClimbPlayRate"),Player,TEXT("PlayRate"));
        }
        Link(Player,TEXT("Pose"),Modes,FName(*FString::Printf(TEXT("BlendPose_%d"),Index+1)));
    }
    if(ArmedLocomotion)
    {FGraphNodeCreator<UAnimGraphNode_Slot> MakeSlot(*Graph);auto* Slot=MakeSlot.CreateNode();MakeSlot.Finalize();Slot->Node.SlotName=TEXT("DefaultSlot");Slot->ReconstructNode();
     Link(Modes,TEXT("Pose"),Slot,TEXT("Source"));Link(Slot,TEXT("Pose"),Root,TEXT("Result"));}
    else Link(Modes,TEXT("Pose"),Root,TEXT("Result"));Root->NodePosX=400;
    if(!Success){UE_LOG(LogTemp,Error,TEXT("RV character AnimGraph pin authoring failed"));return false;}
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);FKismetEditorUtilities::CompileBlueprint(Blueprint);Blueprint->MarkPackageDirty();return Blueprint->Status!=BS_Error;
#else
    return false;
#endif
}




bool URVCharacterContentLibrary::AddWeaponGripIK(UAnimBlueprint* Blueprint,FName PrimaryBone,FName SupportBone)
{
#if WITH_EDITOR
    if(!Blueprint || PrimaryBone.IsNone() || SupportBone.IsNone())return false;
    UEdGraph* Graph=nullptr;for(auto Candidate:Blueprint->FunctionGraphs)if(Candidate->GetFName()==TEXT("AnimGraph"))Graph=Candidate.Get();
    if(!Graph)return false;
    UAnimGraphNode_Root* Root=nullptr;
    for(auto Entry:Graph->Nodes)
    {auto* Node=Entry.Get();if(Node->NodeComment==TEXT("RVWeaponGripIK"))return true;if(auto* R=Cast<UAnimGraphNode_Root>(Node))Root=R;}
    auto* Result=Root?Root->FindPin(TEXT("Result")):nullptr;
    if(!Result || Result->LinkedTo.Num()!=1)return false;
    UEdGraphPin* Source=Result->LinkedTo[0];Result->BreakAllPinLinks();
    const auto* Schema=Graph->GetSchema();bool Success=true;
    auto Link=[&](UEdGraphNode* From,FName Output,UEdGraphNode* To,FName Input)
    {auto* A=From->FindPin(Output);auto* B=To->FindPin(Input);Success=Success && A && B && Schema->TryCreateConnection(A,B);};
    auto Variable=[&](FName Name,int32 Y)
    {FGraphNodeCreator<UK2Node_VariableGet> Make(*Graph);auto* N=Make.CreateNode();N->VariableReference.SetSelfMember(Name);N->NodePosX=400;N->NodePosY=Y;Make.Finalize();return N;};
    FGraphNodeCreator<UAnimGraphNode_LocalToComponentSpace> MakeSpace(*Graph);auto* Space=MakeSpace.CreateNode();MakeSpace.Finalize();Space->NodePosX=550;
    auto* Input=Space->FindPin(TEXT("LocalPose"));Success=Success && Input && Schema->TryCreateConnection(Source,Input);
    auto IK=[&](FName Bone,FName Target,FVector Pole,int32 X)
    {
        FGraphNodeCreator<UAnimGraphNode_TwoBoneIK> Make(*Graph);auto* N=Make.CreateNode();N->Node.IKBone.BoneName=Bone;
        N->Node.EffectorLocationSpace=BCS_ComponentSpace;N->Node.JointTargetLocationSpace=BCS_ComponentSpace;N->Node.JointTargetLocation=Pole;
        N->Node.bAllowStretching=false;N->Node.bMaintainEffectorRelRot=true;N->Node.Alpha=0;
        Make.Finalize();N->ReconstructNode();N->NodePosX=X;
        Link(Variable(Target,300+X/4),Target,N,TEXT("EffectorLocation"));
        Link(Variable(TEXT("WeaponGripIKAlpha"),500+X/4),TEXT("WeaponGripIKAlpha"),N,TEXT("Alpha"));return N;
    };
    auto* Right=IK(PrimaryBone,TEXT("WeaponRightHandTarget"),FVector(-60,-20,110),750);
    auto* Left=IK(SupportBone,TEXT("WeaponLeftHandTarget"),FVector(60,-20,110),1250);
    Left->Node.EffectorLocationSpace=BCS_BoneSpace;Left->Node.EffectorTarget.BoneReference.BoneName=PrimaryBone;
    if(auto* Alpha=Left->FindPin(TEXT("Alpha")))Alpha->BreakAllPinLinks();
    Link(Variable(TEXT("WeaponSupportIKAlpha"),800),TEXT("WeaponSupportIKAlpha"),Left,TEXT("Alpha"));
    FGraphNodeCreator<UAnimGraphNode_ModifyBone> MakeRotation(*Graph);auto* Rotation=MakeRotation.CreateNode();
    Rotation->Node.BoneToModify.BoneName=PrimaryBone;Rotation->Node.RotationMode=BMM_Replace;Rotation->Node.RotationSpace=BCS_ComponentSpace;Rotation->Node.Alpha=0;
    MakeRotation.Finalize();Rotation->ReconstructNode();Rotation->NodePosX=1250;
    Link(Variable(TEXT("WeaponRightHandRotation"),-250),TEXT("WeaponRightHandRotation"),Rotation,TEXT("Rotation"));
    Link(Variable(TEXT("WeaponGripIKAlpha"),-100),TEXT("WeaponGripIKAlpha"),Rotation,TEXT("Alpha"));
    FGraphNodeCreator<UAnimGraphNode_ComponentToLocalSpace> MakeLocal(*Graph);auto* Local=MakeLocal.CreateNode();MakeLocal.Finalize();Local->NodePosX=1500;
    Link(Space,TEXT("ComponentPose"),Right,TEXT("ComponentPose"));Link(Right,TEXT("Pose"),Rotation,TEXT("ComponentPose"));
    Link(Rotation,TEXT("Pose"),Left,TEXT("ComponentPose"));Link(Left,TEXT("Pose"),Local,TEXT("ComponentPose"));Link(Local,TEXT("Pose"),Root,TEXT("Result"));
    Root->NodePosX=1750;
    if(!Success){UE_LOG(LogTemp,Error,TEXT("Weapon IK graph pin link failed"));return false;}
    Space->NodeComment=TEXT("RVWeaponGripIK");FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
    FKismetEditorUtilities::CompileBlueprint(Blueprint);Blueprint->MarkPackageDirty();return Blueprint->Status!=BS_Error;
#else
    return false;
#endif
}
UAnimSequence* URVCharacterContentLibrary::CreateOneHandedAttack(const FString& Path,USkeletalMesh* Mesh,UAnimSequence* Ready,int32 Variant)
{
#if WITH_EDITOR
    if(Variant<0 || Variant>2)return nullptr;
    UAnimSequence* Sequence=CreatePrototypePose(Path,Mesh,{},false,Ready);if(!Sequence)return nullptr;
    auto& Controller=Sequence->GetController();Controller.OpenBracket(FText::FromString(TEXT("One-handed prototype attack")),false);
    const auto& Ref=Mesh->GetRefSkeleton();TArray<FTransform> Base;Base.SetNum(Ref.GetNum());
    for(int32 Bone=0;Bone<Ref.GetNum();++Bone)
    {Base[Bone]=Ref.GetRefBonePose()[Bone];const FName Name=Ref.GetBoneName(Bone);
     if(Ready->GetDataModel()->IsValidBoneTrackName(Name))Base[Bone]=Ready->GetDataModel()->GetBoneTrackTransform(Name,FFrameNumber(0));}
    TMap<FName,TArray<FQuat>> Keys;
    for(int32 Frame=0;Frame<=30;++Frame)
    {
        const float T=Frame/30.f;TArray<FQuat> Global;Global.SetNum(Ref.GetNum());
        for(int32 Bone=0;Bone<Ref.GetNum();++Bone)
        {
            const FName Name=Ref.GetBoneName(Bone);const int32 Parent=Ref.GetParentIndex(Bone);
            const FQuat ParentRotation=Parent==INDEX_NONE?FQuat::Identity:Global[Parent];
            FQuat Local=Base[Bone].GetRotation();Global[Bone]=ParentRotation*Local;
            if(Name==TEXT("upperarm_r") || Name==TEXT("lowerarm_r"))
            {
                const bool Upper=Name==TEXT("upperarm_r");
                const FVector Neutral=Upper?FVector(0,.7,-.7):FVector(0,.7,.7);
                const FVector Wind=Variant==0?(Upper?FVector(-.5,.6,.4):FVector(-.25,.5,.8)):Variant==1?(Upper?FVector(-.7,.6,0):FVector(-.4,.9,.2)):(Upper?FVector(0,.35,.94):FVector(0,.7,.7));
                const FVector Strike=Variant==0?(Upper?FVector(.2,.8,-.2):FVector(.5,.8,-.3)):Variant==1?(Upper?FVector(.3,1,-.15):FVector(.65,.7,-.3)):(Upper?FVector(.05,.8,-.5):FVector(0,.9,-.35));
                const FVector Target=(T<.12f?FMath::Lerp(Neutral,Wind,T/.12f):T<.27f?FMath::Lerp(Wind,Strike,(T-.12f)/.15f):FMath::Lerp(Strike,Neutral,FMath::Clamp((T-.27f)/.48f,0.f,1.f))).GetSafeNormal();
                FVector ChildVector=FVector::ZeroVector;
                for(int32 Child=Bone+1;Child<Ref.GetNum();++Child)if(Ref.GetParentIndex(Child)==Bone && Base[Child].GetTranslation().SizeSquared()>ChildVector.SizeSquared())ChildVector=Base[Child].GetTranslation();
                if(!ChildVector.IsNearlyZero())Global[Bone]=FQuat::FindBetweenNormals(Global[Bone].RotateVector(ChildVector).GetSafeNormal(),Target)*Global[Bone];
                Local=ParentRotation.Inverse()*Global[Bone];Keys.FindOrAdd(Name).Add(Local);
            }
        }
    }
    for(const auto& Pair:Keys)
    {const int32 Index=Ref.FindBoneIndex(Pair.Key);TArray<FVector> Positions,Scales;
     for(int32 Frame=0;Frame<=30;++Frame){Positions.Add(Base[Index].GetLocation());Scales.Add(Base[Index].GetScale3D());}
     Controller.SetBoneTrackKeys(Pair.Key,Positions,Pair.Value,Scales,false);}
    Controller.NotifyPopulated();Controller.CloseBracket(false);Sequence->PostEditChange();Sequence->MarkPackageDirty();return Sequence;
#else
    return nullptr;
#endif
}
bool URVCharacterContentLibrary::BuildOwnerCopyPoseGraph(UAnimBlueprint* Blueprint)
{
#if WITH_EDITOR
    if(!Blueprint)return false;
    UEdGraph* Graph=nullptr;for(auto Candidate:Blueprint->FunctionGraphs)if(Candidate->GetFName()==TEXT("AnimGraph"))Graph=Candidate.Get();
    if(!Graph)return false;
    UAnimGraphNode_Root* Root=nullptr;const auto Old=Graph->Nodes;
    for(auto Entry:Old)if(auto* Node=Cast<UAnimGraphNode_Root>(Entry.Get()))Root=Node;else Graph->RemoveNode(Entry.Get());
    if(!Root)return false;const auto* Schema=Graph->GetSchema();bool OK=true;
    auto Link=[&](UEdGraphNode* A,FName Out,UEdGraphNode* B,FName In){auto* X=A->FindPin(Out);auto* Y=B->FindPin(In);OK=OK && X && Y && Schema->TryCreateConnection(X,Y);};
    FGraphNodeCreator<UAnimGraphNode_CopyPoseFromMesh> MakeCopy(*Graph);auto* Copy=MakeCopy.CreateNode();Copy->Node.bUseAttachedParent=true;MakeCopy.Finalize();
    // Head/neck are masked in pre-skinned vertex space in the owner material.
    // Scaling mixed neck weights to zero creates stretched seam triangles.
    Link(Copy,TEXT("Pose"),Root,TEXT("Result"));
    if(!OK)return false;FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);FKismetEditorUtilities::CompileBlueprint(Blueprint);Blueprint->MarkPackageDirty();return Blueprint->Status!=BS_Error;
#else
    return false;
#endif
}
bool URVCharacterContentLibrary::AddWeaponTwistCorrection(UAnimBlueprint* Blueprint,FName PrimaryBone,const TArray<FName>& TwistBones)
{
#if WITH_EDITOR
    if(!Blueprint)return false;UEdGraph* Graph=nullptr;
    for(auto G:Blueprint->FunctionGraphs)if(G->GetFName()==TEXT("AnimGraph"))Graph=G.Get();if(!Graph)return false;
    UAnimGraphNode_ModifyBone* Rotation=nullptr;
    for(auto Entry:Graph->Nodes)if(auto* N=Cast<UAnimGraphNode_ModifyBone>(Entry.Get());N && N->Node.BoneToModify.BoneName==PrimaryBone && N->Node.RotationMode==BMM_Replace)Rotation=N;
    auto* Source=Rotation?Rotation->FindPin(TEXT("Pose")):nullptr;if(!Source || Source->LinkedTo.Num()!=1)return false;
    auto* Destination=Source->LinkedTo[0];Source->BreakAllPinLinks();const auto* Schema=Graph->GetSchema();bool OK=true;
    for(int32 Index=0;Index<TwistBones.Num();++Index)
    {
        FGraphNodeCreator<UAnimGraphNode_CopyBone> Make(*Graph);auto* N=Make.CreateNode();N->Node.SourceBone.BoneName=PrimaryBone;N->Node.TargetBone.BoneName=TwistBones[Index];
        N->Node.bCopyRotation=true;N->Node.ControlSpace=BCS_ComponentSpace;N->Node.AlphaScaleBias.Scale=Index==0?.67f:.33f;
        Make.Finalize();N->ReconstructNode();N->NodeComment=TEXT("RVWeaponForearmTwist");
        FGraphNodeCreator<UK2Node_VariableGet> MakeAlpha(*Graph);auto* Alpha=MakeAlpha.CreateNode();Alpha->VariableReference.SetSelfMember(TEXT("WeaponGripIKAlpha"));MakeAlpha.Finalize();
        OK=OK && Schema->TryCreateConnection(Source,N->FindPin(TEXT("ComponentPose"))) && Schema->TryCreateConnection(Alpha->FindPin(TEXT("WeaponGripIKAlpha")),N->FindPin(TEXT("Alpha")));
        Source=N->FindPin(TEXT("Pose"));
    }
    OK=OK && Schema->TryCreateConnection(Source,Destination);if(!OK)return false;
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);FKismetEditorUtilities::CompileBlueprint(Blueprint);Blueprint->MarkPackageDirty();return Blueprint->Status!=BS_Error;
#else
    return false;
#endif
}
