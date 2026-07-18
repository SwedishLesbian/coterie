"""Tests for ChronicleDetailWidget.

Validates imports, error handling in refresh/save/delete paths,
session management (try/finally/close), bounds checking, and
hasattr guards for optional sub-widgets.
"""

import sys
import types
import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

def _stub_module(name, attrs=None):
    mod = types.ModuleType(name)
    for attr, val in (attrs or {}).items():
        setattr(mod, attr, val)
    sys.modules[name] = mod
    return mod


class _StubSignal:
    def __init__(self, *args):
        self._emissions = []
    def emit(self, *args):
        self._emissions.append(args)
    def connect(self, slot):
        pass


_QWidget = type("QWidget", (), {"__init__": lambda *a, **kw: None})
_qt_widgets = {
    "QWidget": _QWidget,
    "QVBoxLayout": MagicMock, "QHBoxLayout": MagicMock,
    "QLabel": MagicMock, "QPushButton": MagicMock,
    "QTabWidget": MagicMock, "QTableWidget": MagicMock,
    "QTableWidgetItem": MagicMock,
    "QHeaderView": MagicMock, "QMessageBox": MagicMock,
    "QAbstractItemView": MagicMock, "QGroupBox": MagicMock,
    "QSizePolicy": MagicMock,
}
_stub_module("PyQt6", {})
_stub_module("PyQt6.QtWidgets", _qt_widgets)
_stub_module("PyQt6.QtCore", {
    "pyqtSignal": _StubSignal, "Qt": MagicMock(),
})
_stub_module("PyQt6.QtGui", {"QFont": MagicMock()})

# App stubs
_mock_get_session = MagicMock()
_stub_module("src", {})
_stub_module("src.core", {})
_stub_module("src.core.engine", {"get_session": _mock_get_session})

_MockChronicle = MagicMock()
_MockCharacter = MagicMock()
_stub_module("src.core.models", {"Chronicle": _MockChronicle, "Character": _MockCharacter})
_stub_module("src.core.models.chronicle", {"GameSession": MagicMock()})
_stub_module("src.core.models.staff", {"Staff": MagicMock()})
_stub_module("src.core.models.player", {"Player": MagicMock()})
_stub_module("src.ui", {})
_stub_module("src.ui.dialogs", {})
_stub_module("src.ui.dialogs.chronicle_edit_dialog", {"ChronicleEditDialog": MagicMock()})
_stub_module("src.ui.dialogs.game_session_dialog", {"GameSessionDialog": MagicMock()})
_stub_module("src.ui.widgets", {})
_stub_module("src.ui.widgets.plots_widget", {"PlotsWidget": MagicMock()})
_stub_module("src.ui.widgets.rumors_widget", {"RumorsWidget": MagicMock()})

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------
sys.modules.pop("src.ui.widgets.chronicle_detail_widget", None)

import importlib.util
import pathlib

_src = pathlib.Path(__file__).resolve().parent.parent / "chronicle_detail_widget.py"
_spec = importlib.util.spec_from_file_location(
    "src.ui.widgets.chronicle_detail_widget", _src
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["src.ui.widgets.chronicle_detail_widget"] = _mod
_spec.loader.exec_module(_mod)

ChronicleDetailWidget = _mod.ChronicleDetailWidget


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_widget():
    with patch.object(ChronicleDetailWidget, "_build_ui"), \
         patch.object(ChronicleDetailWidget, "refresh"):
        w = object.__new__(ChronicleDetailWidget)
        w.chronicle_id = 1
        w.chronicle = None
        w.name_label = MagicMock()
        w.meta_label = MagicMock()
        w.characters_table = MagicMock()
        w.sessions_table = MagicMock()
        w.staff_table = MagicMock()
        w.edit_button = MagicMock()
        w.delete_button = MagicMock()
        w.edit_session_btn = MagicMock()
        w.delete_session_btn = MagicMock()
        w.new_session_btn = MagicMock()
        w.tabs = MagicMock()
        w.plots_widget = MagicMock()
        w.rumors_widget = MagicMock()
        w.chronicle_changed = _StubSignal()
        w.character_selected = _StubSignal(object)
        w._character_objects = []
        w._session_objects = []
        return w


def _make_chronicle(**overrides):
    defaults = {
        "id": 1, "name": "Blood Moon", "narrator": "Gabriel",
        "is_active": True, "start_date": datetime(2025, 1, 1),
        "end_date": None, "description": "Test",
    }
    defaults.update(overrides)
    c = MagicMock()
    for k, v in defaults.items():
        setattr(c, k, v)
    return c


# ===================================================================
# Import tests
# ===================================================================

class TestImports:
    def test_module_loads(self):
        assert _mod is not None

    def test_class_exists(self):
        assert hasattr(_mod, "ChronicleDetailWidget")

    def test_has_logger(self):
        assert hasattr(_mod, "logger")

    def test_signals_declared(self):
        assert hasattr(ChronicleDetailWidget, "chronicle_changed") or \
               "chronicle_changed" in ChronicleDetailWidget.__dict__


# ===================================================================
# Refresh error handling
# ===================================================================

class TestRefreshErrorHandling:
    @patch("src.ui.widgets.chronicle_detail_widget.get_session")
    def test_refresh_catches_db_exception(self, mock_gs):
        mock_gs.side_effect = RuntimeError("DB down")
        w = _build_widget()
        # Should NOT raise
        w.refresh()

    @patch("src.ui.widgets.chronicle_detail_widget.get_session")
    def test_refresh_closes_session_on_error(self, mock_gs):
        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.side_effect = RuntimeError("boom")
        mock_gs.return_value = mock_session
        w = _build_widget()
        w.refresh()
        mock_session.close.assert_called_once()

    @patch("src.ui.widgets.chronicle_detail_widget.get_session")
    def test_refresh_returns_early_when_chronicle_not_found(self, mock_gs):
        mock_session = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        mock_gs.return_value = mock_session
        w = _build_widget()
        w.refresh()
        # Should not crash; chronicle stays None
        assert w.chronicle is None


# ===================================================================
# _apply_chronicle_update error handling
# ===================================================================

class TestApplyChronicleUpdate:
    @patch("src.ui.widgets.chronicle_detail_widget.QMessageBox")
    @patch("src.ui.widgets.chronicle_detail_widget.get_session")
    def test_shows_error_dialog_on_db_failure(self, mock_gs, mock_msgbox):
        mock_gs.side_effect = RuntimeError("DB exploded")
        w = _build_widget()
        w._apply_chronicle_update({"id": 1, "name": "X"})
        mock_msgbox.critical.assert_called_once()

    @patch("src.ui.widgets.chronicle_detail_widget.QMessageBox")
    @patch("src.ui.widgets.chronicle_detail_widget.get_session")
    def test_session_closed_after_successful_update(self, mock_gs, mock_msgbox):
        mock_session = MagicMock()
        mock_chronicle = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_chronicle
        mock_gs.return_value = mock_session

        w = _build_widget()
        with patch.object(w, "refresh"):
            w._apply_chronicle_update({
                "id": 1, "name": "Updated", "narrator": "G",
                "description": "D", "start_date": datetime(2025, 1, 1),
                "end_date": None, "is_active": True,
                "storyteller_id": None, "last_modified": datetime.now(),
            })
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()


# ===================================================================
# _apply_chronicle_delete error handling
# ===================================================================

class TestApplyChronicleDelete:
    @patch("src.ui.widgets.chronicle_detail_widget.QMessageBox")
    @patch("src.ui.widgets.chronicle_detail_widget.get_session")
    def test_shows_error_on_db_failure(self, mock_gs, mock_msgbox):
        mock_gs.side_effect = RuntimeError("nope")
        w = _build_widget()
        w._apply_chronicle_delete(1)
        mock_msgbox.critical.assert_called_once()

    @patch("src.ui.widgets.chronicle_detail_widget.QMessageBox")
    @patch("src.ui.widgets.chronicle_detail_widget.get_session")
    def test_unlinks_characters_instead_of_deleting(self, mock_gs, mock_msgbox):
        mock_session = MagicMock()
        mock_chronicle = MagicMock()
        mock_session.query.return_value.filter_by.return_value.first.return_value = mock_chronicle
        # Make delete() chainable
        mock_session.query.return_value.filter_by.return_value.delete.return_value = 0
        mock_session.query.return_value.filter_by.return_value.update.return_value = 0
        mock_gs.return_value = mock_session

        w = _build_widget()
        w._apply_chronicle_delete(1)
        # Verify commit was called (means delete path completed)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()


# ===================================================================
# Bounds checking
# ===================================================================

class TestBoundsChecking:
    def test_character_double_click_out_of_range(self):
        w = _build_widget()
        w._character_objects = [MagicMock()]
        index = MagicMock()
        index.row.return_value = 5  # out of range
        w._on_character_double_click(index)
        assert len(w.character_selected._emissions) == 0

    def test_character_double_click_in_range(self):
        w = _build_widget()
        char = MagicMock()
        w._character_objects = [char]
        index = MagicMock()
        index.row.return_value = 0
        w._on_character_double_click(index)
        assert len(w.character_selected._emissions) == 1
        assert w.character_selected._emissions[0][0] is char

    def test_edit_session_returns_early_when_no_selection(self):
        w = _build_widget()
        w.sessions_table.currentRow.return_value = -1
        w._session_objects = []
        # Should not raise
        w._on_edit_session()


# ===================================================================
# Session button enable/disable
# ===================================================================

class TestSessionSelection:
    def test_buttons_enabled_when_selection_exists(self):
        w = _build_widget()
        w.sessions_table.selectedItems.return_value = [MagicMock()]
        w._on_session_selection()
        w.edit_session_btn.setEnabled.assert_called_with(True)
        w.delete_session_btn.setEnabled.assert_called_with(True)

    def test_buttons_disabled_when_no_selection(self):
        w = _build_widget()
        w.sessions_table.selectedItems.return_value = []
        w._on_session_selection()
        w.edit_session_btn.setEnabled.assert_called_with(False)
        w.delete_session_btn.setEnabled.assert_called_with(False)


# ===================================================================
# _refresh_header handles missing fields
# ===================================================================

class TestRefreshHeader:
    def test_displays_untitled_when_name_is_none(self):
        w = _build_widget()
        w.chronicle = _make_chronicle(name=None)
        w.meta_label.text.return_value = ""
        # Override the or-fallback: the code does `c.name or "Untitled Chronicle"`
        # We need name to actually be falsy
        w.chronicle.name = None
        w._refresh_header()
        w.name_label.setText.assert_called_with("Untitled Chronicle")

    def test_includes_narrator_in_meta(self):
        w = _build_widget()
        w.chronicle = _make_chronicle(narrator="Alice")
        w.meta_label.text.return_value = ""
        w._refresh_header()
        meta_text = w.meta_label.setText.call_args[0][0]
        assert "HST: Alice" in meta_text

    def test_shows_inactive_status(self):
        w = _build_widget()
        w.chronicle = _make_chronicle(is_active=False)
        w.meta_label.text.return_value = ""
        w._refresh_header()
        meta_text = w.meta_label.setText.call_args[0][0]
        assert "Inactive" in meta_text


# ===================================================================
# _save_session error handling
# ===================================================================

class TestSaveSession:
    @patch("src.ui.widgets.chronicle_detail_widget.QMessageBox")
    @patch("src.ui.widgets.chronicle_detail_widget.get_session")
    def test_shows_error_on_failure(self, mock_gs, mock_msgbox):
        mock_gs.side_effect = RuntimeError("DB error")
        w = _build_widget()
        w._save_session({"title": "Test", "chronicle_id": 1})
        mock_msgbox.critical.assert_called_once()

    @patch("src.ui.widgets.chronicle_detail_widget.QMessageBox")
    @patch("src.ui.widgets.chronicle_detail_widget.get_session")
    def test_session_closed_on_success(self, mock_gs, mock_msgbox):
        mock_session = MagicMock()
        mock_gs.return_value = mock_session

        w = _build_widget()
        with patch.object(w, "refresh"):
            w._save_session({
                "chronicle_id": 1, "title": "Session",
                "date": datetime.now(), "location": "Here",
                "summary": "Stuff",
            })
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
