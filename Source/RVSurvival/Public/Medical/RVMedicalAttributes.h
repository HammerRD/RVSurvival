#pragma once
#include "CoreMinimal.h"
#include "AttributeSet.h"
#include "AbilitySystemComponent.h"
#include "RVMedicalAttributes.generated.h"

#define RV_MEDICAL_ACCESSORS(Name) \
    GAMEPLAYATTRIBUTE_PROPERTY_GETTER(URVMedicalAttributes, Name) \
    GAMEPLAYATTRIBUTE_VALUE_GETTER(Name) \
    GAMEPLAYATTRIBUTE_VALUE_SETTER(Name) \
    GAMEPLAYATTRIBUTE_VALUE_INITTER(Name)

/** GAS owns replicated vital attributes and timed medication aggregation. */
UCLASS()
class RVSURVIVAL_API URVMedicalAttributes : public UAttributeSet
{
    GENERATED_BODY()
public:
    URVMedicalAttributes();
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const override;
    virtual void PreAttributeChange(const FGameplayAttribute& Attribute, float& Value) override;
    virtual void PreAttributeBaseChange(const FGameplayAttribute& Attribute, float& Value) const override;
    UPROPERTY(BlueprintReadOnly, SaveGame, ReplicatedUsing=OnRep_Blood) FGameplayAttributeData Blood;
    RV_MEDICAL_ACCESSORS(Blood)
    UPROPERTY(BlueprintReadOnly, SaveGame, ReplicatedUsing=OnRep_Vitality) FGameplayAttributeData Vitality;
    RV_MEDICAL_ACCESSORS(Vitality)
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing=OnRep_Analgesia) FGameplayAttributeData Analgesia;
    RV_MEDICAL_ACCESSORS(Analgesia)
private:
    UFUNCTION() void OnRep_Blood(const FGameplayAttributeData& Previous);
    UFUNCTION() void OnRep_Vitality(const FGameplayAttributeData& Previous);
    UFUNCTION() void OnRep_Analgesia(const FGameplayAttributeData& Previous);
};

