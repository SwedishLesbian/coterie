"""Tests for ChronicleEditDialog.

Covers:
  - _validate disables save when name is empty
  - _validate enables save with a name
  - _on_save emits chronicle_updated with correct data
  - _on_delete emits chronicle_deleted with correct id
  - _load_players handles DB errors gracefully
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.core.models import Chronicle


def _make_mock_chronicle(**overrides):
    """Build a Chronicle-like object for dialog construction."""
    defaults = dict(
        id=1, name="Test Chronicle", narrator="Head ST",
        description="A chronicle", start_date=datetime(2026, 1, 1),
        end_date=None, is_active=True, storyteller_id=None,
    )
    defaults.update(overrides)
    obj = MagicMock(spec=Chronicle)
    for k, v in defaults.items():
        setattr(obj, k, v)
    return obj


class TestValidation:
    """Tests for the _validate method."""

    def test_save_disabled_when_name_empty(self, qapp):
        """Save button should be disabled when the name field is blank."""
        from src.ui.dialogs.chronicle_edit_dialog import ChronicleEditDialog

        chronicle = _make_mock_chronicle()
        with patch.object(ChronicleEditDialog, "_load_players"):
            dialog = ChronicleEditDialog(chronicle)

        dialog.name_edit.setText("")
        dialog._validate()
        assert not dialog.save_button.isEnabled()

    def test_save_enabled_when_name_present(self, qapp):
        """Save button should be enabled when name has text."""
        from src.ui.dialogs.chronicle_edit_dialog import ChronicleEditDialog

        chronicle = _make_mock_chronicle()
        with patch.object(ChronicleEditDialog, "_load_players"):
            dialog = ChronicleEditDialog(chronicle)

        dialog.name_edit.setText("My Chronicle")
        dialog._validate()
        assert dialog.save_button.isEnabled()

    def test_save_disabled_when_name_whitespace_only(self, qapp):
        """Save button should be disabled for whitespace-only name."""
        from src.ui.dialogs.chronicle_edit_dialog import ChronicleEditDialog

        chronicle = _make_mock_chronicle()
        with patch.object(ChronicleEditDialog, "_load_players"):
            dialog = ChronicleEditDialog(chronicle)

        dialog.name_edit.setText("   ")
        dialog._validate()
        assert not dialog.save_button.isEnabled()


class TestOnSave:
    """Tests for _on_save signal emission."""

    def test_emits_chronicle_updated_with_correct_data(self, qapp):
        """_on_save should emit chronicle_updated with a dict of form data."""
        from src.ui.dialogs.chronicle_edit_dialog import ChronicleEditDialog

        chronicle = _make_mock_chronicle(id=42)
        with patch.object(ChronicleEditDialog, "_load_players"):
            dialog = ChronicleEditDialog(chronicle)

        dialog.name_edit.setText("Renamed Chronicle")
        dialog.narrator_edit.setText("New ST")
        dialog.description_edit.setPlainText("Updated desc")

        received = []
        dialog.chronicle_updated.connect(lambda d: received.append(d))

        # Patch accept so dialog doesn't try to close
        with patch.object(dialog, "accept"):
            dialog._on_save()

        assert len(received) == 1
        data = received[0]
        assert data["id"] == 42
        assert data["name"] == "Renamed Chronicle"
        assert data["narrator"] == "New ST"
        assert data["description"] == "Updated desc"
        assert "last_modified" in data


class TestOnDelete:
    """Tests for _on_delete signal emission."""

    def test_emits_chronicle_deleted_on_confirm(self, qapp):
        """_on_delete should emit chronicle_deleted when user confirms."""
        from src.ui.dialogs.chronicle_edit_dialog import ChronicleEditDialog
        from PyQt6.QtWidgets import QMessageBox

        chronicle = _make_mock_chronicle(id=7, name="Doomed")
        with patch.object(ChronicleEditDialog, "_load_players"):
            dialog = ChronicleEditDialog(chronicle)

        received = []
        dialog.chronicle_deleted.connect(lambda cid: received.append(cid))

        with patch.object(dialog, "accept"):
            with patch("src.ui.dialogs.chronicle_edit_dialog.QMessageBox") as mock_mb:
                mock_mb.StandardButton = QMessageBox.StandardButton
                mock_mb.warning.return_value = QMessageBox.StandardButton.Yes
                dialog._on_delete()

        assert received == [7]

    def test_does_not_emit_on_cancel(self, qapp):
        """_on_delete should NOT emit when user cancels the confirmation."""
        from src.ui.dialogs.chronicle_edit_dialog import ChronicleEditDialog
        from PyQt6.QtWidgets import QMessageBox

        chronicle = _make_mock_chronicle(id=7, name="Safe")
        with patch.object(ChronicleEditDialog, "_load_players"):
            dialog = ChronicleEditDialog(chronicle)

        received = []
        dialog.chronicle_deleted.connect(lambda cid: received.append(cid))

        with patch("src.ui.dialogs.chronicle_edit_dialog.QMessageBox") as mock_mb:
            mock_mb.StandardButton = QMessageBox.StandardButton
            mock_mb.warning.return_value = QMessageBox.StandardButton.No
            dialog._on_delete()

        assert received == []


class TestLoadPlayers:
    """Tests for _load_players error handling."""

    def test_handles_db_error_gracefully(self, qapp):
        """_load_players should log a warning, not crash, on DB failure."""
        from src.ui.dialogs.chronicle_edit_dialog import ChronicleEditDialog

        chronicle = _make_mock_chronicle()

        with patch("src.ui.dialogs.chronicle_edit_dialog.get_session") as mock_gs:
            mock_gs.side_effect = Exception("Connection refused")
            # Should not raise
            dialog = ChronicleEditDialog(chronicle)

        # Combo should have at least the "-- None --" entry
        assert dialog.storyteller_combo.count() >= 1
