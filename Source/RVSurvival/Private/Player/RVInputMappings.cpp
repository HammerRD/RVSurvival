#include "Player/RVInputMappings.h"
#include "InputMappingContext.h"
#include "PlayerMappableKeySettings.h"
#include "EnhancedInputSubsystems.h"
#include "UserSettings/EnhancedInputUserSettings.h"
#include "Engine/LocalPlayer.h"
#include "GameFramework/PlayerController.h"
#include "UObject/UnrealType.h"
void RVInputMappings::Map(UInputMappingContext* Context,UInputAction* Action,FKey Key,FName Name,const TCHAR* Label)
{
    auto& Mapping=Context->MapKey(Action,Key);
    // UE5.8 exposes these editable mapping fields to reflection but has no native
    // setter. Configure the same metadata as the editor; never touch runtime key state.
    auto* Settings=NewObject<UPlayerMappableKeySettings>(Context);
    Settings->Name=Name;Settings->DisplayName=FText::FromString(Label);
    Settings->DisplayCategory=FText::FromName(Category(Name));
    auto* Behavior=FindFProperty<FEnumProperty>(FEnhancedActionKeyMapping::StaticStruct(),TEXT("SettingBehavior"));
    auto* Property=FindFProperty<FObjectPropertyBase>(FEnhancedActionKeyMapping::StaticStruct(),TEXT("PlayerMappableKeySettings"));
    check(Behavior && Property);
    Behavior->GetUnderlyingProperty()->SetIntPropertyValue(Behavior->ContainerPtrToValuePtr<void>(&Mapping),uint64(EPlayerMappableKeySettingBehaviors::OverrideSettings));
    Property->SetObjectPropertyValue_InContainer(&Mapping,Settings);
}
void RVInputMappings::Register(APlayerController* Controller,UInputMappingContext* Context)
{
    if(Controller)if(auto* Local=Controller->GetLocalPlayer())
        if(auto* Subsystem=Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
            if(auto* Settings=Subsystem->GetUserSettings())if(!Settings->IsMappingContextRegistered(Context))Settings->RegisterInputMappingContext(Context);
}
void RVInputMappings::Unregister(ULocalPlayer* Local,UInputMappingContext* Context)
{
    if(Local && Context)if(auto* Subsystem=Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
        if(auto* Settings=Subsystem->GetUserSettings())Settings->UnregisterInputMappingContext(Context);
}
FString RVInputMappings::KeyLabel(APlayerController* Controller,FName Name,const TCHAR* Fallback)
{
    if(Controller)if(auto* Local=Controller->GetLocalPlayer())
        if(auto* Subsystem=Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
            if(auto* Settings=Subsystem->GetUserSettings())if(auto* Profile=Settings->GetActiveKeyProfile())
                if(const auto* Row=Profile->GetPlayerMappingRows().Find(Name))
                    for(const auto& Mapping:Row->Mappings)if(Mapping.GetSlot()==EPlayerMappableKeySlot::First)
                        return Mapping.GetCurrentKey().GetDisplayName().ToString();
    return Fallback;
}
FKey RVInputMappings::CurrentKey(APlayerController* PC,FName Name,FKey Fallback)
{if(PC)if(auto* Local=PC->GetLocalPlayer())if(auto* S=Local->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
 if(auto* Settings=S->GetUserSettings())if(auto* P=Settings->GetActiveKeyProfile())if(const auto* Row=P->GetPlayerMappingRows().Find(Name))
 for(const auto& M:Row->Mappings)if(M.GetSlot()==EPlayerMappableKeySlot::First)return M.GetCurrentKey();return Fallback;}
FName RVInputMappings::Category(FName Name)
{
 const FString N=Name.ToString();
 if(N.Contains(TEXT("Weapon")) || N.Contains(TEXT("Melee")) || Name==TEXT("Aim") || Name==TEXT("Fire") || Name==TEXT("Reload") || Name==TEXT("UnloadMagazine"))return TEXT("Combat");
 if(N.StartsWith(TEXT("Move")) || N.StartsWith(TEXT("Look")) || Name==TEXT("Jump") || Name==TEXT("Interact") || Name==TEXT("Sprint") || Name==TEXT("Crouch"))return TEXT("On foot");
 if(Name==TEXT("Medical") || Name==TEXT("Sleep") || Name==TEXT("Stand") || Name==TEXT("Consume"))return TEXT("Medical / survival");
 if(N.StartsWith(TEXT("Inventory")) || Name==TEXT("Transfer") || Name==TEXT("Drop") || Name==TEXT("RefuelItem") || Name==TEXT("Controls") || Name==TEXT("Pause"))return TEXT("UI / inventory");
 return TEXT("RV");
}
