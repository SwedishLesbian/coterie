"""Chronicle model for managing LARP chronicles/campaigns."""

from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

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
    description: Mapped[str] = mapped_column(String)
    start_date: Mapped[datetime] = mapped_column()
    end_date: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    # Storyteller relationship
    storyteller_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    storyteller: Mapped["Player"] = relationship("Player", back_populates="chronicles_run")
    
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