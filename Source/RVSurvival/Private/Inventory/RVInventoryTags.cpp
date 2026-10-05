#include "NativeGameplayTags.h"
#include "Inventory/RVItemDefinition.h"
#include "GameplayTagsManager.h"
FGameplayTag URVItemDefinition::FindRegisteredTag(FName Name)
{ return UGameplayTagsManager::Get().RequestGameplayTag(Name,false); }
// Classification metadata only; no item-specific gameplay dispatch.
UE_DEFINE_GAMEPLAY_TAG_STATIC(RVItemFood, "Item.Category.Food");
UE_DEFINE_GAMEPLAY_TAG_STATIC(RVItemWater, "Item.Category.Water");
UE_DEFINE_GAMEPLAY_TAG_STATIC(RVItemMedical, "Item.Category.Medical");
UE_DEFINE_GAMEPLAY_TAG_STATIC(RVItemAutomotive, "Item.Category.Automotive");
UE_DEFINE_GAMEPLAY_TAG_STATIC(RVItemMaterial, "Item.Category.Material");
UE_DEFINE_GAMEPLAY_TAG_STATIC(RVItemTool, "Item.Category.Tool");
UE_DEFINE_GAMEPLAY_TAG_STATIC(RVItemAmmunition, "Item.Category.Ammunition");
UE_DEFINE_GAMEPLAY_TAG_STATIC(RVItemBulky, "Item.Category.Bulky");
UE_DEFINE_GAMEPLAY_TAG_STATIC(RVItemHandCarry, "Item.Capability.HandCarry");
UE_DEFINE_GAMEPLAY_TAG_STATIC(RVCraftingMetal, "Crafting.Material.Metal");
UE_DEFINE_GAMEPLAY_TAG_STATIC(RVCraftingTool, "Crafting.Tool.General");
