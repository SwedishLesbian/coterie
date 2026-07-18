"""Tests for ChronicleDetailWidget.

Covers:
  - refresh() when chronicle not found (graceful no-op)
  - refresh() with valid data populates header + tables
  - _apply_chronicle_update error path shows QMessageBox.critical
  - _apply_chronicle_delete removes related records
  - _on_delete with no chronicle is a no-op
  - session selection enables/disables edit/delete buttons
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.core.models import Chronicle, Character
from src.core.models.chronicle import GameSession
from src.core.models.staff import Staff


class TestRefresh:
    """Tests for the refresh() data-loading method."""

    def test_refresh_missing_chronicle_does_not_crash(
        self, qapp, db_session
    ):
        """refresh() with a non-existent chronicle_id should silently return."""
        from src.ui.widgets.chronicle_detail_widget import ChronicleDetailWidget

        # Use an ID that doesn't exist
        with patch.object(ChronicleDetailWidget, "refresh", return_value=None):
            widget = ChronicleDetailWidget(chronicle_id=99999)

        # Now call the real refresh -- should not raise
        widget.chronicle_id = 99999
        widget.chronicle = None
        ChronicleDetailWidget.refresh(widget)
        assert widget.chronicle is None

    def test_refresh_populates_header(
        self, qapp, db_session, make_chronicle
    ):
        """refresh() should set the name and meta labels from the chronicle."""
        chronicle = make_chronicle(name="Dark City", narrator="Marcus")

        from src.ui.widgets.chronicle_detail_widget import ChronicleDetailWidget

        with patch.object(ChronicleDetailWidget, "refresh", return_value=None):
            widget = ChronicleDetailWidget(chronicle_id=chronicle.id)

        # Run the real refresh
        ChronicleDetailWidget.refresh(widget)

        assert widget.chronicle is not None
        assert widget.name_label.text() == "Dark City"
        assert "Marcus" in widget.meta_label.text()

    def test_refresh_populates_characters_table(
        self, qapp, db_session, make_chronicle, make_character
    ):
        """refresh() should fill the characters table with chronicle members."""
        chronicle = make_chronicle(name="Night Court")
        make_character(name="Alara", chronicle_id=chronicle.id)
        make_character(name="Brax", chronicle_id=chronicle.id)
        # Third character NOT in this chronicle
        make_character(name="Outsider", chronicle_id=None)

        from src.ui.widgets.chronicle_detail_widget import ChronicleDetailWidget

        with patch.object(ChronicleDetailWidget, "refresh", return_value=None):
            widget = ChronicleDetailWidget(chronicle_id=chronicle.id)

        ChronicleDetailWidget.refresh(widget)
        assert widget.characters_table.rowCount() == 2

    def test_refresh_populates_sessions_table(
        self, qapp, db_session, make_chronicle, make_game_session
    ):
        """refresh() should fill the sessions table."""
        chronicle = make_chronicle(name="Elysium Nights")
        make_game_session(chronicle.id, title="Gathering")
        make_game_session(chronicle.id, title="Blood Hunt")

        from src.ui.widgets.chronicle_detail_widget import ChronicleDetailWidget

        with patch.object(ChronicleDetailWidget, "refresh", return_value=None):
            widget = ChronicleDetailWidget(chronicle_id=chronicle.id)

        ChronicleDetailWidget.refresh(widget)
        assert widget.sessions_table.rowCount() == 2

    def test_refresh_populates_staff_table(
        self, qapp, db_session, make_chronicle, make_staff
    ):
        """refresh() should fill the staff table."""
        chronicle = make_chronicle(name="Kindred Council")
        make_staff(chronicle.id, name="Alice", role="Narrator")
        make_staff(chronicle.id, name="Bob", role="Assistant ST")

        from src.ui.widgets.chronicle_detail_widget import ChronicleDetailWidget

        with patch.object(ChronicleDetailWidget, "refresh", return_value=None):
            widget = ChronicleDetailWidget(chronicle_id=chronicle.id)

        ChronicleDetailWidget.refresh(widget)
        assert widget.staff_table.rowCount() == 2


class TestApplyChronicleUpdate:
    """Tests for _apply_chronicle_update error handling."""

    def test_update_error_shows_critical_messagebox(
        self, qapp, db_session, make_chronicle
    ):
        """When the DB commit fails, a QMessageBox.critical should appear."""
        chronicle = make_chronicle(name="Broken")

        from src.ui.widgets.chronicle_detail_widget import ChronicleDetailWidget

        with patch.object(ChronicleDetailWidget, "refresh", return_value=None):
            widget = ChronicleDetailWidget(chronicle_id=chronicle.id)
        widget.chronicle = chronicle

        bad_data = {"id": chronicle.id, "name": None}  # will cause an error

        with patch("src.ui.widgets.chronicle_detail_widget.QMessageBox") as mock_mb:
            # Force an exception during commit
            with patch("src.ui.widgets.chronicle_detail_widget.get_session") as mock_gs:
                mock_session = MagicMock()
                mock_session.query.return_value.filter_by.return_value.first.side_effect = Exception("DB error")
                mock_gs.return_value = mock_session
                widget._apply_chronicle_update(bad_data)

            mock_mb.critical.assert_called_once()


class TestApplyChronicleDelete:
    """Tests for _apply_chronicle_delete."""

    def test_delete_removes_sessions_and_staff(
        self, qapp, db_session, make_chronicle, make_game_session, make_staff
    ):
        """Deleting a chronicle should remove related sessions and staff."""
        chronicle = make_chronicle(name="Doomed City")
        make_game_session(chronicle.id, title="First Night")
        make_staff(chronicle.id, name="Eve", role="ST")

        from src.ui.widgets.chronicle_detail_widget import ChronicleDetailWidget

        with patch.object(ChronicleDetailWidget, "refresh", return_value=None):
            widget = ChronicleDetailWidget(chronicle_id=chronicle.id)
        widget.chronicle = chronicle

        widget._apply_chronicle_delete(chronicle.id)

        # Verify cleanup
        assert db_session.query(GameSession).filter_by(chronicle_id=chronicle.id).count() == 0
        assert db_session.query(Staff).filter_by(chronicle_id=chronicle.id).count() == 0

    def test_delete_unlinks_characters(
        self, qapp, db_session, make_chronicle, make_character
    ):
        """Characters should have chronicle_id set to None, not deleted."""
        chronicle = make_chronicle(name="Fading Light")
        char = make_character(name="Luna", chronicle_id=chronicle.id)

        from src.ui.widgets.chronicle_detail_widget import ChronicleDetailWidget

        with patch.object(ChronicleDetailWidget, "refresh", return_value=None):
            widget = ChronicleDetailWidget(chronicle_id=chronicle.id)
        widget.chronicle = chronicle

        widget._apply_chronicle_delete(chronicle.id)

        db_session.refresh(char)
        assert char.chronicle_id is None
        # Character still exists
        assert db_session.query(Character).filter_by(id=char.id).first() is not None


class TestOnDelete:
    """Tests for _on_delete guard."""

    def test_on_delete_noop_when_no_chronicle(self, qapp, db_session):
        """_on_delete should do nothing when self.chronicle is None."""
        from src.ui.widgets.chronicle_detail_widget import ChronicleDetailWidget

        with patch.object(ChronicleDetailWidget, "refresh", return_value=None):
            widget = ChronicleDetailWidget(chronicle_id=1)
        widget.chronicle = None

        # Should not raise or show any dialog
        with patch("src.ui.widgets.chronicle_detail_widget.QMessageBox") as mock_mb:
            widget._on_delete()
            mock_mb.warning.assert_not_called()


class TestSessionSelection:
    """Tests for session table selection enabling buttons."""

    def test_buttons_disabled_when_no_selection(self, qapp, db_session, make_chronicle):
        """Edit/Delete session buttons should be disabled with no selection."""
        chronicle = make_chronicle(name="Test")

        from src.ui.widgets.chronicle_detail_widget import ChronicleDetailWidget

        with patch.object(ChronicleDetailWidget, "refresh", return_value=None):
            widget = ChronicleDetailWidget(chronicle_id=chronicle.id)

        # Clear any selection
        widget.sessions_table.clearSelection()
        widget._on_session_selection()

        assert not widget.edit_session_btn.isEnabled()
        assert not widget.delete_session_btn.isEnabled()
