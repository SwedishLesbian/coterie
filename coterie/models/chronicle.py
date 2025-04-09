from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from coterie.models.base import Base, Character

class Chronicle(Base):
    """Chronicle model representing a game chronicle/story."""
    __tablename__ = "chronicles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String)
    narrator: Mapped[str] = mapped_column(String(100))
    start_date: Mapped[datetime] = mapped_column(DateTime)
    last_modified: Mapped[datetime] = mapped_column(DateTime)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    characters: Mapped[List["Character"]] = relationship(
        "Character",
        back_populates="chronicle",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Chronicle {self.name}>" 