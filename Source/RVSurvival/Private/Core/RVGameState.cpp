#include "Core/RVGameState.h"
#include "Engine/World.h"
#include "Net/UnrealNetwork.h"
ARVGameState::ARVGameState() { DifficultyRules=GetDefault<URVDifficultyProfile>()->Rules; }
void ARVGameState::BeginPlay()
{Super::BeginPlay();if(HasAuthority())SetDifficultyAuthority(TEXT("Standard"),NAME_None,1,DifficultyRevision);}
void ARVGameState::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{Super::GetLifetimeReplicatedProps(OutLifetimeProps);DOREPLIFETIME(ARVGameState,DifficultyRules);DOREPLIFETIME(ARVGameState,DifficultyPreset);DOREPLIFETIME(ARVGameState,DifficultyRevision);}
float ARVGameState::Multiplier(const UObject* Context,FName Id)
{if(Context && Context->GetWorld())if(const auto* GS=Context->GetWorld()->GetGameState<ARVGameState>())
    if(const auto* R=GS->DifficultyRules.FindByPredicate([Id](const auto& X){return X.Id==Id;}))return R->Multiplier;
 return 1.f;}
bool ARVGameState::SetDifficultyAuthority(FName Preset,FName Rule,float Value,int32 Expected)
{
    if(!HasAuthority() || Expected!=DifficultyRevision || !FMath::IsFinite(Value))return false;
    if(!Rule.IsNone())
    {auto* R=DifficultyRules.FindByPredicate([Rule](const auto& X){return X.Id==Rule;});if(!R || Value<R->Minimum || Value>R->Maximum)return false;
     R->Multiplier=Value;DifficultyPreset=TEXT("Custom");}
    else
    {const auto* Profile=DifficultyPresets.FindByPredicate([Preset](const auto& P){return P && P->Preset==Preset;});
     if(Profile)DifficultyRules=(*Profile)->Rules;
     else if(Preset==TEXT("Standard"))DifficultyRules=GetDefault<URVDifficultyProfile>()->Rules;
     else return false;
     for(auto& R:DifficultyRules)R.Multiplier=FMath::Clamp(FMath::IsFinite(R.Multiplier)?R.Multiplier:1.f,R.Minimum,R.Maximum);
     DifficultyPreset=Preset;}
    ++DifficultyRevision;ForceNetUpdate();return true;
}
