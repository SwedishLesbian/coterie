"""Player model for Coterie."""

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .character import Character
    from .chronicle import Chronicle

class Player(Base):
    """Model representing a player in a chronicle."""
    __tablename__ = "players"
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Active")
    
    # Relationships
    chronicles_run: Mapped[List["Chronicle"]] = relationship(
        "Chronicle",
        back_populates="storyteller",
        foreign_keys="Chronicle.storyteller_id"
    )
    characters: Mapped[List["Character"]] = relationship(
        "Character",
        back_populates="player"
    )
    
    def __repr__(self) -> str:
        return f"<Player(name='{self.name}', status='{self.status}')>" 