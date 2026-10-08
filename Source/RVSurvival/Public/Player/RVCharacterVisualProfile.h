#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Medical/RVMedicalProfile.h"
#include "RVCharacterVisualProfile.generated.h"
class USkeletalMesh;
class UAnimInstance;
USTRUCT(BlueprintType)
struct FRVBodyRegionBones
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly) ERVBodyRegion Region=ERVBodyRegion::Torso;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName AnchorBone;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TArray<FName> Roots;
};
USTRUCT(BlueprintType)
struct FRVEquipmentAnchor
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName Id;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName Bone;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FTransform Offset;
};
/** Replaceable visual configuration; no item, injury, movement or seat authority. */
UCLASS(BlueprintType)
class RVSURVIVAL_API URVCharacterVisualProfile : public UPrimaryDataAsset
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<USkeletalMesh> Body;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TSubclassOf<UAnimInstance> AnimationClass;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FVector Scale=FVector::OneVector;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FRotator MeshRotation=FRotator(0,-90,0);
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FVector StandingOffset=FVector::ZeroVector;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FVector SeatedOffset=FVector(0,0,-25);
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FRotator BedMeshRotation=FRotator(0,-90,0);
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FVector BedOffset=FVector(85,0,-15);
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FVector DownedOffset=FVector(85,0,4);
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FName OwnerHiddenHead;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) FVector OwnerCameraOffset=FVector(20,0,0);
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TArray<FRVBodyRegionBones> BodyRegions;
    UPROPERTY(EditAnywhere, BlueprintReadOnly) TArray<FRVEquipmentAnchor> EquipmentAnchors;
};
