"""Character model for Coterie."""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .chronicle import session_attendance

if TYPE_CHECKING:
    from .chronicle import Chronicle, GameSession
    from .player import Player
    from .larp_trait import LarpTrait
    from .trait import Trait

class Character(Base):
    """Base character class for all World of Darkness characters."""
    __tablename__ = "characters"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    nature: Mapped[str] = mapped_column(String(50))
    demeanor: Mapped[str] = mapped_column(String(50))
    player_name: Mapped[str] = mapped_column(String(100))  # Renamed from player to avoid confusion
    status: Mapped[str] = mapped_column(String(50))
    narrator: Mapped[str] = mapped_column(String(100))
    is_npc: Mapped[bool] = mapped_column(Boolean, default=False)
    start_date: Mapped[datetime] = mapped_column(DateTime)
    last_modified: Mapped[datetime] = mapped_column(DateTime)
    biography: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(String(2000))
    
    # Chronicle relationship
    chronicle_id: Mapped[Optional[int]] = mapped_column(ForeignKey("chronicles.id"), nullable=True)
    
    # Player relationship
    player_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"), nullable=True)
    
    # Common attributes
    willpower: Mapped[int] = mapped_column(Integer, default=0)
    temp_willpower: Mapped[int] = mapped_column(Integer, default=0)
    
    # Experience points
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    xp_unspent: Mapped[int] = mapped_column(Integer, default=0)
    
    # Discriminator column for polymorphic identity
    type: Mapped[str] = mapped_column(String(50))
    
    # Relationships
    chronicle: Mapped[Optional["Chronicle"]] = relationship(back_populates="characters")
    player: Mapped[Optional["Player"]] = relationship(back_populates="characters")
    larp_traits: Mapped[List["LarpTrait"]] = relationship(back_populates="character")
    traits: Mapped[List["Trait"]] = relationship(back_populates="character")
    attended_sessions: Mapped[List["GameSession"]] = relationship(
        secondary=session_attendance,
        back_populates="attending_characters"
    )

    __mapper_args__ = {
        "polymorphic_identity": "character",
        "polymorphic_on": "type",
    }

    def __repr__(self) -> str:
        return f"<Character {self.name} ({self.player_name})>" 