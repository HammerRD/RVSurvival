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
    Settings->DisplayCategory=FText::FromString(TEXT("RV controls"));
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
