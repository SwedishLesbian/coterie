"""Tests for GameSessionDialog.

Covers:
  - Dialog initializes in create vs edit mode
  - _validate disables save on empty title
  - _on_save emits session_saved with correct fields
  - _populate_fields handles missing/partial data
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestInitialization:
    """Tests for dialog initialization modes."""

    def test_create_mode_title(self, qapp):
        """In create mode, window title should say 'New Game Session'."""
        from src.ui.dialogs.game_session_dialog import GameSessionDialog
        dialog = GameSessionDialog(chronicle_id=1)
        assert "New" in dialog.windowTitle()
        assert not dialog._editing

    def test_edit_mode_title(self, qapp):
        """In edit mode, window title should say 'Edit Game Session'."""
        from src.ui.dialogs.game_session_dialog import GameSessionDialog
        data = {"id": 1, "title": "Old Session", "date": datetime(2026, 2, 1),
                "location": "Hall", "summary": "Stuff"}
        dialog = GameSessionDialog(chronicle_id=1, session_data=data)
        assert "Edit" in dialog.windowTitle()
        assert dialog._editing

    def test_edit_mode_save_button_label(self, qapp):
        """In edit mode, save button should say 'Save'."""
        from src.ui.dialogs.game_session_dialog import GameSessionDialog
        data = {"id": 1, "title": "Old", "date": datetime(2026, 2, 1),
                "location": "", "summary": ""}
        dialog = GameSessionDialog(chronicle_id=1, session_data=data)
        assert dialog.save_button.text() == "Save"

    def test_create_mode_save_button_label(self, qapp):
        """In create mode, save button should say 'Create'."""
        from src.ui.dialogs.game_session_dialog import GameSessionDialog
        dialog = GameSessionDialog(chronicle_id=1)
        assert dialog.save_button.text() == "Create"


class TestValidation:
    """Tests for _validate method."""

    def test_save_disabled_when_title_empty(self, qapp):
        from src.ui.dialogs.game_session_dialog import GameSessionDialog
        dialog = GameSessionDialog(chronicle_id=1)
        dialog.title_edit.setText("")
        dialog._validate()
        assert not dialog.save_button.isEnabled()

    def test_save_enabled_when_title_present(self, qapp):
        from src.ui.dialogs.game_session_dialog import GameSessionDialog
        dialog = GameSessionDialog(chronicle_id=1)
        dialog.title_edit.setText("Blood Hunt")
        dialog._validate()
        assert dialog.save_button.isEnabled()

    def test_save_disabled_when_title_whitespace(self, qapp):
        from src.ui.dialogs.game_session_dialog import GameSessionDialog
        dialog = GameSessionDialog(chronicle_id=1)
        dialog.title_edit.setText("   ")
        dialog._validate()
        assert not dialog.save_button.isEnabled()


class TestOnSave:
    """Tests for _on_save signal emission."""

    def test_emits_session_saved_with_fields(self, qapp):
        from src.ui.dialogs.game_session_dialog import GameSessionDialog
        dialog = GameSessionDialog(chronicle_id=5)
        dialog.title_edit.setText("Gathering of Clans")
        dialog.location_edit.setText("The Elysium")
        dialog.summary_edit.setPlainText("A tense negotiation.")

        received = []
        dialog.session_saved.connect(lambda d: received.append(d))

        with patch.object(dialog, "accept"):
            dialog._on_save()

        assert len(received) == 1
        data = received[0]
        assert data["title"] == "Gathering of Clans"
        assert data["location"] == "The Elysium"
        assert data["summary"] == "A tense negotiation."
        assert data["chronicle_id"] == 5
        assert "date" in data

    def test_emits_id_when_editing(self, qapp):
        from src.ui.dialogs.game_session_dialog import GameSessionDialog
        existing = {"id": 99, "title": "Old", "date": datetime(2026, 2, 1),
                    "location": "", "summary": ""}
        dialog = GameSessionDialog(chronicle_id=5, session_data=existing)

        received = []
        dialog.session_saved.connect(lambda d: received.append(d))

        with patch.object(dialog, "accept"):
            dialog._on_save()

        assert received[0].get("id") == 99


class TestPopulateFields:
    """Tests for _populate_fields with partial data."""

    def test_partial_data_fills_available_fields(self, qapp):
        from src.ui.dialogs.game_session_dialog import GameSessionDialog
        data = {"id": 1, "title": "Partial", "date": None,
                "location": None, "summary": None}
        dialog = GameSessionDialog(chronicle_id=1, session_data=data)
        assert dialog.title_edit.text() == "Partial"
        assert dialog.location_edit.text() == ""
        assert dialog.summary_edit.toPlainText() == ""

    def test_missing_keys_use_defaults(self, qapp):
        from src.ui.dialogs.game_session_dialog import GameSessionDialog
        data = {"id": 1, "title": "Minimal"}
        dialog = GameSessionDialog(chronicle_id=1, session_data=data)
        assert dialog.title_edit.text() == "Minimal"
