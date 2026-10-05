# Inventory plan
Not implemented until Gate 4. URVItemDefinition will be a Data Asset with stable ID, tags, presentation, mass, volume, stack/category and condition support. Runtime instances carry unique identity, quantity, condition and definition reference.

URVInventoryComponent will validate mutations/transfers on authority and replicate changes, preferably a Fast Array, rather than per-frame full contents. Backpack and RV storage share the same rules. Equipment remains separate. Heavy carryables remain world actors. Never dispatch behavior using display-name strings.
