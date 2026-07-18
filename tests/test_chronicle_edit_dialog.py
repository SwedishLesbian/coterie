"""Tests for ChronicleEditDialog.

Validates imports, error handling in _load_players, validation logic,
signal emissions on save/delete, and field population.
"""

import sys
import types
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


# ---------------------------------------------------------------------------
# Stub out heavy dependencies so tests run without PyQt6 / DB installed
# ---------------------------------------------------------------------------


def _stub_module(name, attrs=None):
    """Create a stub module and register it in sys.modules."""
    mod = types.ModuleType(name)
    for attr, val in (attrs or {}).items():
        setattr(mod, attr, val)
    sys.modules[name] = mod
    return mod


class _StubSignal:
    """Minimal pyqtSignal replacement that records emit() calls."""

    def __init__(self, *args):
        self._emissions = []

    def emit(self, *args):
        self._emissions.append(args)

    def connect(self, slot):
        pass


# PyQt6 stubs
_QDialog = type("QDialog", (), {"__init__": lambda *a, **kw: None, "accept": lambda self: None, "reject": lambda self: None, "setWindowTitle": lambda *a: None, "setMinimumWidth": lambda *a: None, "setMinimumHeight": lambda *a: None})
_qt_widgets = {
    "QDialog": _QDialog,
    "QVBoxLayout": MagicMock, "QHBoxLayout": MagicMock,
    "QFormLayout": MagicMock,
    "QLineEdit": MagicMock, "QTextEdit": MagicMock,
    "QDateEdit": MagicMock, "QCheckBox": MagicMock,
    "QComboBox": MagicMock, "QPushButton": MagicMock,
    "QLabel": MagicMock, "QMessageBox": MagicMock,
    "QWidget": type("QWidget", (), {"__init__": lambda *a, **kw: None}),
    "QGroupBox": MagicMock,
}
_stub_module("PyQt6", {})
_stub_module("PyQt6.QtWidgets", _qt_widgets)
_stub_module("PyQt6.QtCore", {
    "pyqtSignal": _StubSignal, "Qt": MagicMock(), "QDate": MagicMock(),
})
_stub_module("PyQt6.QtGui", {"QFont": MagicMock()})

# App stubs
_stub_module("src", {})
_stub_module("src.core", {})
_stub_module("src.core.engine", {"get_session": MagicMock()})
_stub_module("src.core.models", {"Chronicle": MagicMock})
_stub_module("src.core.models.player", {"Player": MagicMock})

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------
sys.modules.pop("src.ui.dialogs.chronicle_edit_dialog", None)

import importlib.util
import pathlib

_src = pathlib.Path(__file__).resolve().parent.parent / "chronicle_edit_dialog.py"
_spec = importlib.util.spec_from_file_location(
    "src.ui.dialogs.chronicle_edit_dialog", _src
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["src.ui.dialogs.chronicle_edit_dialog"] = _mod
_spec.loader.exec_module(_mod)

ChronicleEditDialog = _mod.ChronicleEditDialog


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_chronicle(**overrides):
    defaults = {
        "id": 1, "name": "Blood Moon", "narrator": "Gabriel",
        "description": "A dark tale", "is_active": True,
        "start_date": datetime(2025, 1, 1), "end_date": None,
        "storyteller_id": None,
    }
    defaults.update(overrides)
    c = MagicMock()
    for k, v in defaults.items():
        setattr(c, k, v)
    return c


def _build_dialog(chronicle=None):
    c = chronicle or _make_chronicle()
    with patch.object(ChronicleEditDialog, "_build_ui"), \
         patch.object(ChronicleEditDialog, "_populate_fields"), \
         patch.object(ChronicleEditDialog, "_connect_signals"):
        dlg = object.__new__(ChronicleEditDialog)
        dlg.chronicle = c
        dlg.name_edit = MagicMock()
        dlg.narrator_edit = MagicMock()
        dlg.description_edit = MagicMock()
        dlg.start_date_edit = MagicMock()
        dlg.end_date_edit = MagicMock()
        dlg.is_active_check = MagicMock()
        dlg.storyteller_combo = MagicMock()
        dlg.save_button = MagicMock()
        dlg.cancel_button = MagicMock()
        dlg.delete_button = MagicMock()
        dlg.chronicle_updated = _StubSignal(dict)
        dlg.chronicle_deleted = _StubSignal(int)
        return dlg


# ===================================================================
# Import tests
# ===================================================================

class TestImports:
    def test_module_loads(self):
        assert _mod is not None

    def test_class_exists(self):
        assert hasattr(_mod, "ChronicleEditDialog")

    def test_has_logger(self):
        assert hasattr(_mod, "logger")


# ===================================================================
# Validation tests
# ===================================================================

class TestValidation:
    def test_save_disabled_when_name_empty(self):
        dlg = _build_dialog()
        dlg.name_edit.text.return_value = "   "
        dlg._validate()
        dlg.save_button.setEnabled.assert_called_with(False)

    def test_save_enabled_when_name_present(self):
        dlg = _build_dialog()
        dlg.name_edit.text.return_value = "Blood Moon"
        dlg._validate()
        dlg.save_button.setEnabled.assert_called_with(True)

    def test_save_disabled_when_name_only_whitespace(self):
        dlg = _build_dialog()
        dlg.name_edit.text.return_value = "\t\n"
        dlg._validate()
        dlg.save_button.setEnabled.assert_called_with(False)


# ===================================================================
# Save action tests
# ===================================================================

class TestOnSave:
    def test_emits_chronicle_updated_with_correct_fields(self):
        dlg = _build_dialog()
        dlg.name_edit.text.return_value = "New Name"
        dlg.narrator_edit.text.return_value = "Narrator"
        dlg.description_edit.toPlainText.return_value = "Desc"
        dlg.is_active_check.isChecked.return_value = True
        dlg.storyteller_combo.currentData.return_value = 42

        start_qdate = MagicMock()
        start_qdate.year.return_value = 2025
        start_qdate.month.return_value = 6
        start_qdate.day.return_value = 15
        dlg.start_date_edit.date.return_value = start_qdate

        end_qdate = MagicMock()
        dlg.end_date_edit.date.return_value = end_qdate
        dlg.end_date_edit.minimumDate.return_value = end_qdate

        dlg.accept = MagicMock()
        dlg._on_save()

        assert len(dlg.chronicle_updated._emissions) == 1
        data = dlg.chronicle_updated._emissions[0][0]
        assert data["name"] == "New Name"
        assert data["narrator"] == "Narrator"
        assert data["storyteller_id"] == 42
        assert data["is_active"] is True
        assert data["end_date"] is None
        assert data["id"] == 1
        assert "last_modified" in data
        dlg.accept.assert_called_once()

    def test_end_date_populated_when_not_minimum(self):
        dlg = _build_dialog()
        dlg.name_edit.text.return_value = "X"
        dlg.narrator_edit.text.return_value = ""
        dlg.description_edit.toPlainText.return_value = ""
        dlg.is_active_check.isChecked.return_value = False
        dlg.storyteller_combo.currentData.return_value = None

        start_qdate = MagicMock()
        start_qdate.year.return_value = 2025
        start_qdate.month.return_value = 1
        start_qdate.day.return_value = 1
        dlg.start_date_edit.date.return_value = start_qdate

        end_qdate = MagicMock()
        end_qdate.year.return_value = 2026
        end_qdate.month.return_value = 3
        end_qdate.day.return_value = 8
        dlg.end_date_edit.date.return_value = end_qdate
        dlg.end_date_edit.minimumDate.return_value = MagicMock()

        dlg.accept = MagicMock()
        dlg._on_save()

        data = dlg.chronicle_updated._emissions[0][0]
        assert isinstance(data["end_date"], datetime)
        assert data["end_date"].year == 2026


# ===================================================================
# Delete action tests
# ===================================================================

class TestOnDelete:
    @patch("src.ui.dialogs.chronicle_edit_dialog.QMessageBox")
    def test_delete_emits_on_yes(self, mock_msgbox):
        mock_msgbox.StandardButton.Yes = 1
        mock_msgbox.StandardButton.No = 0
        mock_msgbox.warning.return_value = 1

        dlg = _build_dialog()
        dlg.accept = MagicMock()
        dlg._on_delete()

        assert len(dlg.chronicle_deleted._emissions) == 1
        assert dlg.chronicle_deleted._emissions[0][0] == 1
        dlg.accept.assert_called_once()

    @patch("src.ui.dialogs.chronicle_edit_dialog.QMessageBox")
    def test_delete_does_not_emit_on_no(self, mock_msgbox):
        mock_msgbox.StandardButton.Yes = 1
        mock_msgbox.StandardButton.No = 0
        mock_msgbox.warning.return_value = 0

        dlg = _build_dialog()
        dlg.accept = MagicMock()
        dlg._on_delete()

        assert len(dlg.chronicle_deleted._emissions) == 0
        dlg.accept.assert_not_called()


# ===================================================================
# _load_players error handling
# ===================================================================

class TestLoadPlayersErrorHandling:
    @patch("src.ui.dialogs.chronicle_edit_dialog.get_session")
    def test_db_error_is_caught_and_logged(self, mock_get_session):
        mock_get_session.side_effect = RuntimeError("DB is gone")
        dlg = _build_dialog()
        dlg.storyteller_combo = MagicMock()
        # Should NOT raise
        dlg._load_players()

    @patch("src.ui.dialogs.chronicle_edit_dialog.get_session")
    def test_session_closed_on_query_error(self, mock_get_session):
        mock_session = MagicMock()
        mock_session.query.side_effect = RuntimeError("query boom")
        mock_get_session.return_value = mock_session
        dlg = _build_dialog()
        dlg.storyteller_combo = MagicMock()
        dlg._load_players()
        mock_session.close.assert_called_once()


# ===================================================================
# Populate fields tests
# ===================================================================

class TestPopulateFields:
    def test_handles_none_name(self):
        dlg = _build_dialog(_make_chronicle(name=None))
        dlg._populate_fields()
        dlg.name_edit.setText.assert_called_with("")

    def test_handles_none_narrator(self):
        dlg = _build_dialog(_make_chronicle(narrator=None))
        dlg._populate_fields()
        dlg.narrator_edit.setText.assert_called_with("")

    def test_handles_none_description(self):
        dlg = _build_dialog(_make_chronicle(description=None))
        dlg._populate_fields()
        dlg.description_edit.setPlainText.assert_called_with("")

    def test_handles_none_is_active_defaults_true(self):
        dlg = _build_dialog(_make_chronicle(is_active=None))
        dlg._populate_fields()
        dlg.is_active_check.setChecked.assert_called_with(True)

    def test_storyteller_combo_set_when_id_present(self):
        dlg = _build_dialog(_make_chronicle(storyteller_id=5))
        dlg.storyteller_combo.findData.return_value = 2
        dlg._populate_fields()
        dlg.storyteller_combo.setCurrentIndex.assert_called_with(2)

    def test_storyteller_combo_not_set_when_not_found(self):
        dlg = _build_dialog(_make_chronicle(storyteller_id=999))
        dlg.storyteller_combo.findData.return_value = -1
        dlg._populate_fields()
        dlg.storyteller_combo.setCurrentIndex.assert_not_called()
