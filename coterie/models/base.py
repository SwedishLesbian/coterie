"""Base model and common utilities."""

from typing import TYPE_CHECKING
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    from .larp_trait import LarpTrait
    from .character import Character
    from .player import Player
    from .chronicle import Chronicle, GameSession

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass 