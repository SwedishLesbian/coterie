"""Pytest fixtures for synchronous UI tests.

Provides an in-memory SQLite database via SQLAlchemy (synchronous),
mocks for get_session / init_db so UI widgets never touch the real
database, and a headless QApplication instance for PyQt6.
"""

import os
import sys
import pytest
from unittest.mock import patch
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.models.base import Base
from src.core.models import Chronicle, Character
from src.core.models.chronicle import GameSession
from src.core.models.staff import Staff
from src.core.models.player import Player


@pytest.fixture(scope="session")
def db_engine():
    """Create a one-per-test-run in-memory SQLite engine."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    """Yield a transactional session that rolls back after every test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    factory = sessionmaker(bind=connection)
    session = factory()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def _patch_engine(db_session):
    """Auto-patch get_session / init_db everywhere the UI imports them."""
    targets = [
        "src.core.engine.get_session",
        "src.ui.widgets.chronicle_detail_widget.get_session",
        "src.ui.dialogs.chronicle_edit_dialog.get_session",
        "src.ui.main_window.get_session",
    ]
    active = []
    for t in targets:
        try:
            p = patch(t, return_value=db_session)
            p.start()
            active.append(p)
        except (AttributeError, ModuleNotFoundError):
            pass

    init_targets = [
        "src.core.engine.init_db",
        "src.ui.main_window.init_db",
    ]
    for t in init_targets:
        try:
            p = patch(t, return_value=None)
            p.start()
            active.append(p)
        except (AttributeError, ModuleNotFoundError):
            pass

    yield

    for p in active:
        try:
            p.stop()
        except RuntimeError:
            pass


@pytest.fixture(scope="session")
def qapp():
    """Create or reuse a QApplication for the test session."""
    if "DISPLAY" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"

    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture()
def make_chronicle(db_session):
    """Factory that inserts a Chronicle and returns it."""
    def _factory(name="Test Chronicle", narrator="Head ST", is_active=True,
                 start_date=None, **kwargs):
        c = Chronicle(
            name=name, narrator=narrator,
            description=kwargs.pop("description", "A test chronicle"),
            start_date=start_date or datetime(2026, 1, 1),
            is_active=is_active, **kwargs,
        )
        db_session.add(c)
        db_session.flush()
        return c
    return _factory


@pytest.fixture()
def make_character(db_session):
    """Factory that inserts a Character and returns it."""
    def _factory(name="Test Char", chronicle_id=None, char_type="vampire",
                 status="Active", **kwargs):
        ch = Character(
            name=name, chronicle_id=chronicle_id,
            type=char_type, status=status, **kwargs,
        )
        db_session.add(ch)
        db_session.flush()
        return ch
    return _factory


@pytest.fixture()
def make_game_session(db_session):
    """Factory that inserts a GameSession and returns it."""
    def _factory(chronicle_id, title="Session 1", **kwargs):
        gs = GameSession(
            chronicle_id=chronicle_id, title=title,
            date=kwargs.pop("date", datetime(2026, 3, 1)),
            summary=kwargs.pop("summary", "Things happened."),
            location=kwargs.pop("location", "The Elysium"),
            **kwargs,
        )
        db_session.add(gs)
        db_session.flush()
        return gs
    return _factory


@pytest.fixture()
def make_staff(db_session):
    """Factory that inserts a Staff record and returns it."""
    def _factory(chronicle_id, name="Alice", role="Narrator", **kwargs):
        s = Staff(chronicle_id=chronicle_id, name=name, role=role, **kwargs)
        db_session.add(s)
        db_session.flush()
        return s
    return _factory


@pytest.fixture()
def make_player(db_session):
    """Factory that inserts a Player record and returns it."""
    def _factory(name="Player One", **kwargs):
        p = Player(name=name, **kwargs)
        db_session.add(p)
        db_session.flush()
        return p
    return _factory
