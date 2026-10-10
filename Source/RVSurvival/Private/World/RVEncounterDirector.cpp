#include "World/RVEncounterDirector.h"
#include "Combat/RVInfected.h"
#include "Combat/RVInfectedProfile.h"
#include "Core/RVGameState.h"
#include "Engine/World.h"
bool URVEncounterDirector::Claim(FGuid Id,AActor* Zone)
{
 if(!Id.IsValid() || !IsValid(Zone) || !Zone->HasAuthority())return false;
 if(const auto* Existing=Zones.Find(Id);Existing && Existing->IsValid() && Existing->Get()!=Zone)return false;
 Zones.Add(Id,Zone);return true;
}
void URVEncounterDirector::Release(FGuid Id,AActor* Zone)
{if(const auto* Existing=Zones.Find(Id);Existing && Existing->Get()==Zone)Zones.Remove(Id);}
int32 URVEncounterDirector::ActiveCount()
{ActiveInfected.RemoveAll([](const auto& I){return !I.IsValid();});return ActiveInfected.Num();}
FRVEncounterSnapshot& URVEncounterDirector::SelectAuthority(FGuid Id,const URVEncounterProfile* Profile,const TArray<FVector>& Positions)
{
 auto& Record=Encounters.FindOrAdd(Id);if(Record.bSelected)return Record;
 if(GetWorld()->GetNetMode()==NM_Client)return Record;
 Record.bSelected=true;
 if(!Profile || GetWorld()->GetTimeSeconds()<NextEventTime)return Record;
 if(!Profile->Choices.ContainsByPredicate([](const auto& Choice){return Choice.Outcome==ERVEncounterOutcome::Quiet && FMath::IsFinite(Choice.Weight) && Choice.Weight>0;}))
 {UE_LOG(LogTemp,Warning,TEXT("Encounter profile %s lacks weighted quiet travel; choosing quiet"),*GetNameSafe(Profile));return Record;}
 FRandomStream Random(GetTypeHash(Id));float Total=0;
 for(const auto& Choice:Profile->Choices)
  if(FMath::IsFinite(Choice.Weight))Total+=FMath::Max(0.f,Choice.Weight)*(Recent.Num()>0 && Recent.Last()==Choice.Outcome?.35f:1.f);
 float Roll=Random.FRand()*Total;const FRVEncounterChoice* Selected=nullptr;
 for(const auto& Choice:Profile->Choices)
 {
  const float Weight=FMath::IsFinite(Choice.Weight)?FMath::Max(0.f,Choice.Weight):0.f;
  Roll-=Weight*(Recent.Num()>0 && Recent.Last()==Choice.Outcome?.35f:1.f);
  if(Weight>0 && Roll<0){Selected=&Choice;break;}
 }
 if(!Selected)return Record;
 Record.Outcome=Selected->Outcome;
 if(Record.Outcome==ERVEncounterOutcome::InfectedCluster)
 {
  const int32 Count=FMath::Clamp(FMath::CeilToInt(FMath::Clamp(Selected->InfectedCount,0,6)*ARVGameState::Multiplier(this,TEXT("Population"))),0,FMath::Min(6,Positions.Num()));
  for(int32 I=0;I<Count;++I){FRVRegionInfectedSnapshot Member;Member.Position=Positions[I];Member.Vitality=Profile->InfectedProfile?Profile->InfectedProfile->Vitality:65;Record.Infected.Add(Member);}
 }
 if(Record.Outcome!=ERVEncounterOutcome::Quiet)NextEventTime=GetWorld()->GetTimeSeconds()+FMath::Clamp(Profile->EventCooldown,30.f,600.f);
 Recent.Add(Record.Outcome);if(Recent.Num()>3)Recent.RemoveAt(0);
 return Record;
}
