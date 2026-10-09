#include "Core/RVDifficultyProfile.h"
URVDifficultyProfile::URVDifficultyProfile()
{
    auto Add=[this](const TCHAR* Id,const TCHAR* Label,const TCHAR* Help,const TCHAR* Group,float Min=.25f,float Max=3.f,bool Future=false)
    {FRVDifficultyRule R;R.Id=Id;R.Label=FText::FromString(Label);R.Description=FText::FromString(Help);R.Group=Group;R.Minimum=Min;R.Maximum=Max;R.bPreparationOnly=Future;Rules.Add(R);};
    Add(TEXT("Hunger"),TEXT("Hunger rate"),TEXT("How quickly nutrition decreases over time."),TEXT("Survival"));
    Add(TEXT("Thirst"),TEXT("Thirst rate"),TEXT("How quickly hydration decreases over time."),TEXT("Survival"));
    Add(TEXT("Fatigue"),TEXT("Fatigue rate"),TEXT("How quickly waking activity increases fatigue."),TEXT("Survival"));
    Add(TEXT("DamageTaken"),TEXT("Player damage taken"),TEXT("Scales incoming injury damage, including infected attacks."),TEXT("Consequences"));
    Add(TEXT("Bleeding"),TEXT("Bleeding rate"),TEXT("Scales blood loss from existing bleeding wounds."),TEXT("Consequences"));
    Add(TEXT("Fracture"),TEXT("Fracture severity"),TEXT("Scales fracture consequences where injury rules apply."),TEXT("Consequences"));
    Add(TEXT("Recovery"),TEXT("Recovery speed"),TEXT("Scales rest and medical recovery; does not restore food or water."),TEXT("Consequences"));
    Add(TEXT("InfectedDamage"),TEXT("Infected damage"),TEXT("Scales infected attack damage before player damage scaling."),TEXT("Combat"));
    Add(TEXT("InfectedDurability"),TEXT("Infected durability"),TEXT("Modest health scaling; infected remain grounded physical targets."),TEXT("Combat"),.5f,1.5f);
    Add(TEXT("InfectedPerception"),TEXT("Infected perception"),TEXT("Scales native infected sight and hearing range."),TEXT("Combat"),.5f,1.5f);
    Add(TEXT("Fuel"),TEXT("RV fuel consumption"),TEXT("How much gasoline the running/driving RV consumes."),TEXT("RV"));
    Add(TEXT("GeneratorFuel"),TEXT("Generator fuel consumption"),TEXT("How much gasoline the generator consumes while running."),TEXT("RV"));
    Add(TEXT("Mechanical"),TEXT("Mechanical damage severity"),TEXT("Scales existing thermal engine damage; does not add random failures."),TEXT("RV"));
    Add(TEXT("Thermal"),TEXT("Thermal stress"),TEXT("Scales heat produced by the running engine."),TEXT("RV"));
    Add(TEXT("Loot"),TEXT("Loot abundance"),TEXT("Future world configuration only; no generated loot system exists yet."),TEXT("Future world"),.25f,3.f,true);
    Add(TEXT("Population"),TEXT("Infected population"),TEXT("Future world configuration only; does not spawn test-map infected."),TEXT("Future world"),.25f,3.f,true);
}
