#include "Medical/RVAnalgesicEffect.h"
#include "Medical/RVMedicalAttributes.h"
#include "NativeGameplayTags.h"
UE_DEFINE_GAMEPLAY_TAG_STATIC(TAG_RVMedicationRelief,"Medical.Medication.PainRelief");
URVAnalgesicEffect::URVAnalgesicEffect()
{
    DurationPolicy=EGameplayEffectDurationType::HasDuration;
    DurationMagnitude=FScalableFloat(300);
    FGameplayModifierInfo Modifier;
    Modifier.Attribute=URVMedicalAttributes::GetAnalgesiaAttribute();
    Modifier.ModifierOp=EGameplayModOp::Additive;
    FSetByCallerFloat Magnitude; Magnitude.DataTag=TAG_RVMedicationRelief;
    Modifier.ModifierMagnitude=FGameplayEffectModifierMagnitude(Magnitude);
    Modifiers.Add(Modifier);
}
