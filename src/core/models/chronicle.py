"""Chronicle model for managing LARP chronicles/campaigns."""

from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, ForeignKey, Table, Column, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.base import Base

if TYPE_CHECKING:
    from .player import Player
    from .character import Character
    from .staff import Staff

# Association table for tracking character attendance at game sessions
session_attendance = Table(
    "session_attendance",
    Base.metadata,
    Column("character_id", ForeignKey("characters.id"), primary_key=True),
    Column("session_id", ForeignKey("game_sessions.id"), primary_key=True),
    extend_existing=True
)

class Chronicle(Base):
    """A chronicle/campaign in which characters participate."""
    __tablename__ = "chronicles"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True, default="")
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # HST/Narrator name (text field for quick access)
    narrator: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="")
    last_modified: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Optional storyteller relationship (player who runs the chronicle)
    storyteller_id: Mapped[Optional[int]] = mapped_column(ForeignKey("players.id"), nullable=True)
    storyteller: Mapped[Optional["Player"]] = relationship("Player", back_populates="chronicles_run")


    # Characters in this chronicle
    characters: Mapped[List["Character"]] = relationship("Character", back_populates="chronicle")

    # Game sessions
    sessions: Mapped[List["GameSession"]] = relationship("GameSession", back_populates="chronicle")

    # Staff members
    staff: Mapped[List["Staff"]] = relationship("Staff", back_populates="chronicle")

class GameSession(Base):
    """Represents a single game session within a chronicle."""
    __tablename__ = "game_sessions"
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True)
    chronicle_id: Mapped[int] = mapped_column(ForeignKey("chronicles.id"))
    date: Mapped[datetime]
    title: Mapped[str] = mapped_column(String(100))
    summary: Mapped[Optional[str]] = mapped_column(String(2000))
    location: Mapped[Optional[str]] = mapped_column(String(200))

    # Relationships
    chronicle: Mapped["Chronicle"] = relationship(back_populates="sessions")
    attending_characters: Mapped[List["Character"]] = relationship(
        secondary=session_attendance,
        back_populates="attended_sessions"
    )

    def __repr__(self) -> str:
        return f"<GameSession {self.title} ({self.date})>" 