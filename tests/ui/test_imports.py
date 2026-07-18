"""Validate that all UI module imports resolve without errors.

These tests catch broken imports early -- missing dependencies,
circular imports, or typos in import paths.
"""

import importlib
import pytest


MODULES_UNDER_TEST = [
    "src.ui.main_window",
    "src.ui.widgets.chronicle_detail_widget",
    "src.ui.dialogs.chronicle_edit_dialog",
    "src.ui.dialogs.game_session_dialog",
    "src.ui.dialogs.character_creation",
    "src.ui.dialogs.chronicle_creation",
    "src.ui.dialogs.data_manager_dialog",
    "src.ui.widgets.character_list_widget",
    "src.ui.widgets.plots_widget",
    "src.ui.widgets.rumors_widget",
    "src.ui.sheets.vampire_sheet",
    "src.core.engine",
    "src.core.models",
    "src.core.models.chronicle",
    "src.core.models.character",
    "src.core.models.staff",
    "src.core.models.player",
    "src.utils.data_loader",
]


@pytest.mark.parametrize("module_path", MODULES_UNDER_TEST)
def test_import_resolves(module_path, qapp):
    """Each module should import without raising."""
    mod = importlib.import_module(module_path)
    assert mod is not None


class TestMainWindowImports:
    """Verify key symbols exist after importing main_window."""

    def test_main_window_class_exists(self, qapp):
        from src.ui.main_window import MainWindow
        assert MainWindow is not None

    def test_main_window_has_qfiledialog(self, qapp):
        """QFileDialog was added today for Grapevine import."""
        from PyQt6.QtWidgets import QFileDialog
        assert QFileDialog is not None

    def test_chronicle_detail_widget_class_exists(self, qapp):
        from src.ui.widgets.chronicle_detail_widget import ChronicleDetailWidget
        assert ChronicleDetailWidget is not None

    def test_chronicle_edit_dialog_class_exists(self, qapp):
        from src.ui.dialogs.chronicle_edit_dialog import ChronicleEditDialog
        assert ChronicleEditDialog is not None

    def test_game_session_dialog_class_exists(self, qapp):
        from src.ui.dialogs.game_session_dialog import GameSessionDialog
        assert GameSessionDialog is not None


class TestChronicleDetailWidgetImports:
    """Verify ChronicleDetailWidget pulls in all expected dependencies."""

    def test_imports_game_session_model(self, qapp):
        from src.core.models.chronicle import GameSession
        assert GameSession is not None

    def test_imports_staff_model(self, qapp):
        from src.core.models.staff import Staff
        assert Staff is not None

    def test_imports_chronicle_edit_dialog(self, qapp):
        from src.ui.dialogs.chronicle_edit_dialog import ChronicleEditDialog
        assert ChronicleEditDialog is not None

    def test_imports_game_session_dialog(self, qapp):
        from src.ui.dialogs.game_session_dialog import GameSessionDialog
        assert GameSessionDialog is not None

    def test_imports_plots_and_rumors_widgets(self, qapp):
        from src.ui.widgets.plots_widget import PlotsWidget
        from src.ui.widgets.rumors_widget import RumorsWidget
        assert PlotsWidget is not None
        assert RumorsWidget is not None
