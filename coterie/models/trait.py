"""Base trait model for Coterie."""

from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .character import Character

class Trait(Base):
    """Base class for character traits."""
    __tablename__ = "traits"
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    name: Mapped[str] = mapped_column(String(100))
    value: Mapped[int] = mapped_column(Integer, default=0)
    note: Mapped[Optional[str]] = mapped_column(String)
    category: Mapped[str] = mapped_column(String(50))  # physical, social, mental, etc.
    type: Mapped[str] = mapped_column(String(50))  # ability, influence, background, etc.
    
    # Relationships
    character: Mapped["Character"] = relationship("Character", back_populates="traits")
    
    __mapper_args__ = {
        "polymorphic_identity": "trait",
        "polymorphic_on": "type",
    } 