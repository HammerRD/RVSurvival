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
#include "AnimGraphNode_BlendListByInt.h"
#include "AnimGraphNode_BlendSpacePlayer.h"
#include "AnimGraphNode_SequencePlayer.h"
#include "K2Node_VariableGet.h"
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
bool URVCharacterContentLibrary::BuildAnimationGraph(UAnimBlueprint* Blueprint,UBlendSpace* Locomotion,const TArray<UAnimSequence*>& Poses)
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
    Link(Variable(TEXT("PoseIndex"),-200),TEXT("PoseIndex"),Modes,TEXT("ActiveChildIndex"));Link(Walk,TEXT("Pose"),Modes,TEXT("BlendPose_0"));
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
    Link(Modes,TEXT("Pose"),Root,TEXT("Result"));Root->NodePosX=400;
    if(!Success){UE_LOG(LogTemp,Error,TEXT("RV character AnimGraph pin authoring failed"));return false;}
    FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);FKismetEditorUtilities::CompileBlueprint(Blueprint);Blueprint->MarkPackageDirty();return Blueprint->Status!=BS_Error;
#else
    return false;
#endif
}


