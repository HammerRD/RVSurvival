#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "RVCharacterContentLibrary.generated.h"
class USkeletalMesh;
class UAnimSequence;
class UAnimBlueprint;
class UBlendSpace;
/** Editor authoring bridge to native Unreal animation tools; no runtime graph engine. */
UCLASS()
class RVSURVIVAL_API URVCharacterContentLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly)) static UAnimSequence* CreatePrototypePose(const FString& AssetPath,USkeletalMesh* Mesh,const TMap<FName,FRotator>& BoneRotations,bool Climbing=false,UAnimSequence* BasePose=nullptr);
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly)) static bool PopulateLocomotion(UBlendSpace* BlendSpace,const TArray<UAnimSequence*>& Clips,const TArray<FVector>& Coordinates);
    UFUNCTION(BlueprintCallable,meta=(DevelopmentOnly)) static bool BuildAnimationGraph(UAnimBlueprint* Blueprint,UBlendSpace* Locomotion,const TArray<UAnimSequence*>& Poses);
};
