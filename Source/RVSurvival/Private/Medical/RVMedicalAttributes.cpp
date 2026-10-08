#include "Medical/RVMedicalAttributes.h"
#include "Net/UnrealNetwork.h"
URVMedicalAttributes::URVMedicalAttributes() { InitBlood(100); InitVitality(100); InitAnalgesia(0); }
void URVMedicalAttributes::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME_CONDITION_NOTIFY(URVMedicalAttributes, Blood, COND_None, REPNOTIFY_Always);
    DOREPLIFETIME_CONDITION_NOTIFY(URVMedicalAttributes, Vitality, COND_None, REPNOTIFY_Always);
    DOREPLIFETIME_CONDITION_NOTIFY(URVMedicalAttributes, Analgesia, COND_None, REPNOTIFY_Always);
}
void URVMedicalAttributes::PreAttributeChange(const FGameplayAttribute& Attribute, float& Value)
{ Super::PreAttributeChange(Attribute, Value); Value=FMath::IsFinite(Value)?FMath::Clamp(Value,0.f,100.f):0.f; }
void URVMedicalAttributes::PreAttributeBaseChange(const FGameplayAttribute& Attribute, float& Value) const
{ Super::PreAttributeBaseChange(Attribute, Value); Value=FMath::IsFinite(Value)?FMath::Clamp(Value,0.f,100.f):0.f; }
void URVMedicalAttributes::OnRep_Blood(const FGameplayAttributeData& Previous) { GAMEPLAYATTRIBUTE_REPNOTIFY(URVMedicalAttributes,Blood,Previous); }
void URVMedicalAttributes::OnRep_Vitality(const FGameplayAttributeData& Previous) { GAMEPLAYATTRIBUTE_REPNOTIFY(URVMedicalAttributes,Vitality,Previous); }
void URVMedicalAttributes::OnRep_Analgesia(const FGameplayAttributeData& Previous) { GAMEPLAYATTRIBUTE_REPNOTIFY(URVMedicalAttributes,Analgesia,Previous); }
