"""Tests for GameSessionDialog.

Validates imports, validation logic, signal emission on save,
field population for edit mode, and create-vs-edit branching.
"""

import sys
import types
import pytest
from unittest.mock import MagicMock, patch
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


_QDialog = type("QDialog", (), {
    "__init__": lambda *a, **kw: None,
    "accept": lambda self: None, "reject": lambda self: None,
    "setWindowTitle": lambda *a: None,
    "setMinimumWidth": lambda *a: None, "setMinimumHeight": lambda *a: None,
})

_qt_widgets = {
    "QDialog": _QDialog,
    "QVBoxLayout": MagicMock, "QHBoxLayout": MagicMock,
    "QFormLayout": MagicMock,
    "QLineEdit": MagicMock, "QTextEdit": MagicMock,
    "QDateEdit": MagicMock,
    "QPushButton": MagicMock, "QLabel": MagicMock,
    "QWidget": type("QWidget", (), {"__init__": lambda *a, **kw: None}),
    "QGroupBox": MagicMock,
}
_stub_module("PyQt6", {})
_stub_module("PyQt6.QtWidgets", _qt_widgets)
_stub_module("PyQt6.QtCore", {
    "pyqtSignal": _StubSignal, "QDate": MagicMock(),
})
_stub_module("PyQt6.QtGui", {"QFont": MagicMock()})

# ---------------------------------------------------------------------------
# Import the module under test
# ---------------------------------------------------------------------------
sys.modules.pop("src.ui.dialogs.game_session_dialog", None)

import importlib.util
import pathlib

_src = pathlib.Path(__file__).resolve().parent.parent / "game_session_dialog.py"
_spec = importlib.util.spec_from_file_location(
    "src.ui.dialogs.game_session_dialog", _src
)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["src.ui.dialogs.game_session_dialog"] = _mod
_spec.loader.exec_module(_mod)

GameSessionDialog = _mod.GameSessionDialog


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_dialog(chronicle_id=1, session_data=None):
    with patch.object(GameSessionDialog, "_build_ui"), \
         patch.object(GameSessionDialog, "_populate_fields"), \
         patch.object(GameSessionDialog, "_connect_signals"):
        dlg = object.__new__(GameSessionDialog)
        dlg.chronicle_id = chronicle_id
        dlg.session_data = session_data
        dlg._editing = session_data is not None
        dlg.title_edit = MagicMock()
        dlg.date_edit = MagicMock()
        dlg.location_edit = MagicMock()
        dlg.summary_edit = MagicMock()
        dlg.save_button = MagicMock()
        dlg.cancel_button = MagicMock()
        dlg.session_saved = _StubSignal(dict)
        return dlg


# ===================================================================
# Import tests
# ===================================================================

class TestImports:
    def test_module_loads(self):
        assert _mod is not None

    def test_class_exists(self):
        assert hasattr(_mod, "GameSessionDialog")

    def test_has_logger(self):
        assert hasattr(_mod, "logger")


# ===================================================================
# Validation
# ===================================================================

class TestValidation:
    def test_save_disabled_when_title_empty(self):
        dlg = _build_dialog()
        dlg.title_edit.text.return_value = "  "
        dlg._validate()
        dlg.save_button.setEnabled.assert_called_with(False)

    def test_save_enabled_when_title_present(self):
        dlg = _build_dialog()
        dlg.title_edit.text.return_value = "Gathering"
        dlg._validate()
        dlg.save_button.setEnabled.assert_called_with(True)


# ===================================================================
# Save action
# ===================================================================

class TestOnSave:
    def test_emits_session_saved_in_create_mode(self):
        dlg = _build_dialog(chronicle_id=7)
        dlg.title_edit.text.return_value = "Session One"
        dlg.location_edit.text.return_value = "The Haven"
        dlg.summary_edit.toPlainText.return_value = "Things happened"

        qdate = MagicMock()
        qdate.year.return_value = 2025
        qdate.month.return_value = 6
        qdate.day.return_value = 15
        dlg.date_edit.date.return_value = qdate

        dlg.accept = MagicMock()
        dlg._on_save()

        assert len(dlg.session_saved._emissions) == 1
        data = dlg.session_saved._emissions[0][0]
        assert data["chronicle_id"] == 7
        assert data["title"] == "Session One"
        assert data["location"] == "The Haven"
        assert "id" not in data
        dlg.accept.assert_called_once()

    def test_carries_forward_id_in_edit_mode(self):
        existing = {"id": 42, "title": "Old", "date": datetime(2025, 1, 1),
                     "location": "X", "summary": "Y"}
        dlg = _build_dialog(chronicle_id=1, session_data=existing)
        dlg.title_edit.text.return_value = "Updated"
        dlg.location_edit.text.return_value = "New Place"
        dlg.summary_edit.toPlainText.return_value = "New summary"

        qdate = MagicMock()
        qdate.year.return_value = 2025
        qdate.month.return_value = 3
        qdate.day.return_value = 1
        dlg.date_edit.date.return_value = qdate

        dlg.accept = MagicMock()
        dlg._on_save()

        data = dlg.session_saved._emissions[0][0]
        assert data["id"] == 42


# ===================================================================
# Populate fields
# ===================================================================

class TestPopulateFields:
    def test_does_nothing_when_session_data_is_none(self):
        dlg = _build_dialog(session_data=None)
        dlg.session_data = None
        dlg._populate_fields()
        dlg.title_edit.setText.assert_not_called()

    def test_populates_title_and_location(self):
        data = {"title": "The Ball", "location": "Elysium",
                "summary": "Dancing", "date": datetime(2025, 6, 1)}
        dlg = _build_dialog(session_data=data)
        dlg._populate_fields()
        dlg.title_edit.setText.assert_called_with("The Ball")
        dlg.location_edit.setText.assert_called_with("Elysium")

    def test_handles_missing_date(self):
        data = {"title": "X", "location": "", "summary": ""}
        dlg = _build_dialog(session_data=data)
        # date key missing -- should not raise
        dlg._populate_fields()

    def test_handles_non_datetime_date(self):
        data = {"title": "X", "location": "", "summary": "", "date": "not-a-date"}
        dlg = _build_dialog(session_data=data)
        dlg._populate_fields()
        # date_edit.setDate should NOT be called for non-datetime
        dlg.date_edit.setDate.assert_not_called()


# ===================================================================
# Create vs Edit mode
# ===================================================================

class TestCreateVsEditMode:
    def test_editing_flag_false_for_new(self):
        dlg = _build_dialog(session_data=None)
        assert dlg._editing is False

    def test_editing_flag_true_for_existing(self):
        dlg = _build_dialog(session_data={"id": 1, "title": "X"})
        assert dlg._editing is True
