Chronicle-card selection does not reliably navigate to or scope the character list, and newly added negative traits are dropped during character creation. Duplicate-level display also remains incorrect.

Full review comments:

- [P1] Open the Characters tab instead of selecting index 1 — /mnt/d/TheEdge/KingslayerTM/Coterie/src/ui/main_window.py:502-502
  On a normal startup the only tab is Chronicle at index 0; `characters_widget` is created but is not added until the Game > Characters action is used. Therefore clicking a chronicle card calls `setCurrentIndex(1)` with no such tab and leaves the user on the chronicle screen rather than showing its characters. Locate or add `characters_widget` before selecting it.

- [P1] Filter the character list by the active chronicle — /mnt/d/TheEdge/KingslayerTM/Coterie/src/ui/main_window.py:504-505
  Selecting a chronicle invokes this refresh, but `_refresh_characters` still queries `session.query(Character).all()` and applies no `active_chronicle` condition. Consequently, once the Characters tab is visible, the card action displays characters from every chronicle rather than the selected chronicle.

- [P2] Serialize selected negative traits — /mnt/d/TheEdge/KingslayerTM/Coterie/src/ui/dialogs/character_creation.py:273-276
  Traits selected in this new widget are never added to `get_character_data()`: that method serializes attributes, abilities, disciplines, backgrounds, merits, and flaws, but never calls `self.negative_traits.get_category_traits()`. Thus the emitted creation data contains no negative-trait selections, so they are discarded when the dialog is accepted.

- [P2] Consolidate duplicate trait levels into one row — /mnt/d/TheEdge/KingslayerTM/Coterie/src/ui/widgets/larp_trait_widget.py:82-90
  When a user selects the same ability twice, this appends `Melee x2` while retaining the original `Melee`, so the UI shows two rows instead of the requested single `Melee x2` row. Further additions create additional rows (`Melee x3`, etc.), and removing one level cannot reliably reduce the displayed aggregate.
