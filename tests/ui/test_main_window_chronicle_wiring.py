"""Tests for MainWindow chronicle wiring.

Covers:
  - Tab tracking (open_chronicle_tabs, open_character_sheets)
  - _close_tab index decrement logic
  - _on_chronicle_card_clicked opens new tab vs focuses existing
  - _refresh_characters filters by active_chronicle
  - _import_grapevine handles cancel and valid file
  - _refresh_chronicles error path
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime


def _make_main_window(qapp):
    """Create a MainWindow with heavy deps mocked out."""
    with patch("src.ui.main_window.get_session") as mock_gs, \
         patch("src.ui.main_window.init_db"), \
         patch("src.ui.main_window.CharacterListWidget"), \
         patch("src.ui.main_window.PlotsWidget"), \
         patch("src.ui.main_window.RumorsWidget"), \
         patch("src.ui.main_window.VampireSheet"), \
         patch("src.ui.main_window.CharacterCreationDialog"), \
         patch("src.ui.main_window.ChronicleCreationDialog"), \
         patch("src.ui.main_window.DataManagerDialog"):

        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.count.return_value = 0
        mock_gs.return_value = mock_session

        from src.ui.main_window import MainWindow
        window = MainWindow()
        return window, mock_session


class TestTabTracking:
    """Tests for open_chronicle_tabs and open_character_sheets tracking."""

    def test_initial_tab_dicts_are_empty(self, qapp):
        window, _ = _make_main_window(qapp)
        assert window.open_chronicle_tabs == {}
        assert window.open_character_sheets == {}


class TestCloseTab:
    """Tests for _close_tab index decrement logic."""

    def test_close_tab_decrements_higher_indices(self, qapp):
        """Closing a tab should decrement indices of tabs above it."""
        window, _ = _make_main_window(qapp)

        # Simulate three open chronicle tabs at indices 1, 2, 3
        window.open_chronicle_tabs = {10: 1, 20: 2, 30: 3}
        window.open_character_sheets = {}

        # Add dummy tabs so removeTab doesn't fail
        from PyQt6.QtWidgets import QWidget
        for _ in range(4):
            window.tabs.addTab(QWidget(), "dummy")

        # Close tab at index 2 (chronicle_id=20)
        window._close_tab(2)

        # chronicle 20 should be gone; 30 should decrement 3->2
        assert 20 not in window.open_chronicle_tabs
        assert window.open_chronicle_tabs[10] == 1
        assert window.open_chronicle_tabs[30] == 2

    def test_close_tab_removes_character_sheet(self, qapp):
        """Closing a character sheet tab should remove it from tracking."""
        window, _ = _make_main_window(qapp)

        window.open_character_sheets = {5: 1}
        window.open_chronicle_tabs = {}

        from PyQt6.QtWidgets import QWidget
        for _ in range(3):
            window.tabs.addTab(QWidget(), "dummy")

        window._close_tab(1)
        assert 5 not in window.open_character_sheets

    def test_close_tab_decrements_cross_dicts(self, qapp):
        """Closing a chronicle tab should decrement character sheet indices above it."""
        window, _ = _make_main_window(qapp)

        window.open_chronicle_tabs = {10: 1}
        window.open_character_sheets = {99: 3}

        from PyQt6.QtWidgets import QWidget
        for _ in range(5):
            window.tabs.addTab(QWidget(), "dummy")

        window._close_tab(1)

        assert 10 not in window.open_chronicle_tabs
        assert window.open_character_sheets[99] == 2  # decremented from 3


class TestOnChronicleCardClicked:
    """Tests for _on_chronicle_card_clicked tab management."""

    def test_opens_new_tab_for_new_chronicle(self, qapp):
        """Clicking a chronicle card should open a new tab."""
        window, _ = _make_main_window(qapp)

        chronicle = MagicMock()
        chronicle.id = 42
        chronicle.name = "Dark City"

        initial_count = window.tabs.count()

        with patch("src.ui.main_window.ChronicleDetailWidget") as MockDetail:
            MockDetail.return_value = MagicMock()
            window._on_chronicle_card_clicked(chronicle)

        assert chronicle.id in window.open_chronicle_tabs
        assert window.tabs.count() > initial_count

    def test_focuses_existing_tab_on_reclick(self, qapp):
        """Clicking the same chronicle again should focus the existing tab."""
        window, _ = _make_main_window(qapp)

        chronicle = MagicMock()
        chronicle.id = 42
        chronicle.name = "Dark City"

        with patch("src.ui.main_window.ChronicleDetailWidget") as MockDetail:
            MockDetail.return_value = MagicMock()
            window._on_chronicle_card_clicked(chronicle)
            tab_count_after_first = window.tabs.count()

            window._on_chronicle_card_clicked(chronicle)
            assert window.tabs.count() == tab_count_after_first


class TestRefreshCharactersFiltering:
    """Tests for _refresh_characters active chronicle filtering."""

    def test_no_active_chronicle_queries_all(self, qapp):
        """Without an active chronicle, all characters should be queried."""
        window, mock_session = _make_main_window(qapp)
        window.active_chronicle = None

        mock_query = MagicMock()
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query

        window._refresh_characters()

        # Should call .all() without .filter()
        mock_query.all.assert_called()

    def test_active_chronicle_filters_query(self, qapp):
        """With an active chronicle, characters should be filtered by chronicle_id."""
        window, mock_session = _make_main_window(qapp)

        mock_chronicle = MagicMock()
        mock_chronicle.id = 7
        window.active_chronicle = mock_chronicle

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_filter.all.return_value = []
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query

        window._refresh_characters()

        mock_query.filter.assert_called_once()


class TestImportGrapevine:
    """Tests for _import_grapevine flow."""

    def test_cancel_does_nothing(self, qapp):
        """Cancelling the file dialog should be a no-op."""
        window, _ = _make_main_window(qapp)

        with patch("src.ui.main_window.QFileDialog") as mock_fd:
            mock_fd.getOpenFileName.return_value = ("", "")
            window._import_grapevine()

        # No error, no status change beyond what's already there

    def test_valid_file_calls_loader(self, qapp):
        """Selecting a valid file should call load_grapevine_file."""
        window, _ = _make_main_window(qapp)

        with patch("src.ui.main_window.QFileDialog") as mock_fd, \
             patch("src.ui.main_window.load_grapevine_file") as mock_load, \
             patch("src.ui.main_window.QMessageBox"):
            mock_fd.getOpenFileName.return_value = ("/tmp/test.gv", "Grapevine Files (*.gv)")
            mock_load.return_value = 5  # 5 characters imported
            window._import_grapevine()

        mock_load.assert_called_once()


class TestRefreshChroniclesError:
    """Tests for _refresh_chronicles error path."""

    def test_db_error_shows_critical_messagebox(self, qapp):
        """When get_session raises, a QMessageBox.critical should appear."""
        window, _ = _make_main_window(qapp)

        with patch("src.ui.main_window.get_session") as mock_gs, \
             patch("src.ui.main_window.QMessageBox") as mock_mb:
            mock_gs.side_effect = Exception("DB gone")
            window._refresh_chronicles()

        mock_mb.critical.assert_called_once()
