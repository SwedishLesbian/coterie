from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Character(Base):
    """Base character class for all World of Darkness characters."""
    __tablename__ = "characters"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    nature: Mapped[str] = mapped_column(String(50))
    demeanor: Mapped[str] = mapped_column(String(50))
    player: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50))
    narrator: Mapped[str] = mapped_column(String(100))
    is_npc: Mapped[bool] = mapped_column(Boolean, default=False)
    start_date: Mapped[datetime] = mapped_column(DateTime)
    last_modified: Mapped[datetime] = mapped_column(DateTime)
    biography: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(String)
    
    # Common attributes
    willpower: Mapped[int] = mapped_column(Integer, default=0)
    temp_willpower: Mapped[int] = mapped_column(Integer, default=0)
    
    # Experience points
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    xp_unspent: Mapped[int] = mapped_column(Integer, default=0)
    
    # Discriminator column for polymorphic identity
    type: Mapped[str] = mapped_column(String(50))
    
    __mapper_args__ = {
        "polymorphic_identity": "character",
        "polymorphic_on": "type",
    }

class Trait(Base):
    """Base class for character traits."""
    __tablename__ = "traits"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    name: Mapped[str] = mapped_column(String(100))
    value: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[Optional[str]] = mapped_column(String)
    category: Mapped[str] = mapped_column(String(50))  # physical, social, mental, etc.
    type: Mapped[str] = mapped_column(String(50))  # ability, influence, background, etc.
    
    character: Mapped["Character"] = relationship(back_populates="traits")

# Add the relationship to Character
Character.traits: Mapped[List[Trait]] = relationship(
    back_populates="character",
    cascade="all, delete-orphan"
) 