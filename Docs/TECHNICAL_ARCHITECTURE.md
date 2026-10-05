# Technical architecture
One runtime C++ module, with Core, Player, Interaction and UI boundaries. Future Inventory, Equipment, Survival, Vehicles, Crafting, AI, World, Encounters, Factions, Save and Debug areas are added when their gates require them, not as speculative managers.

GameInstance is a campaign/session lifecycle extension point. GameMode chooses pawn/controller/state/HUD classes and owns server rules. GameState and PlayerState are typed framework extension points; they deliberately add no speculative replicated state. Character composes Camera and Interaction and uses stock CharacterMovement network prediction. PlayerController remains the ownership/input framework boundary.

IRVInteractable offers side-effect-free permission/text/duration queries and authority-only start/complete/cancel events. URVInteractionComponent performs local focus queries and authoritative retraces. RVTestInteractable owns a replicated counter. Temporary HUD only reads prompt state; UMG content replaces presentation later. Gameplay never depends on the HUD.

Enhanced Input mappings are transient assets created per pawn, retained by UPROPERTY, installed only in its local-player subsystem, and removed at teardown. No plugin beyond Enhanced Input is needed for Gate 1. Chaos, World Partition, Gameplay Tags and Data Assets enter the architecture when their concrete gate requires them.
