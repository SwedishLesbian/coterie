"""LARP trait model for Mind's Eye Theater trait system.

This module implements the LARP trait system used in Mind's Eye Theater,
where traits are represented by adjectives rather than numeric values.
"""

from typing import List, Optional, Set, TYPE_CHECKING
from sqlalchemy import String, Integer, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .character import Character

# Association table for trait categories
trait_categories = Table(
    "trait_categories",
    Base.metadata,
    Column("category_id", ForeignKey("trait_category.id"), primary_key=True),
    Column("trait_id", ForeignKey("larp_traits.id"), primary_key=True),
    extend_existing=True
)

class TraitCategory(Base):
    """Category for organizing LARP traits."""
    __tablename__ = "trait_category"
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("trait_category.id"), nullable=True)
    
    # Relationship to traits
    traits: Mapped[List["LarpTrait"]] = relationship(
        "LarpTrait",
        secondary=trait_categories,
        back_populates="categories"
    )
    subcategories: Mapped[List["TraitCategory"]] = relationship(
        "TraitCategory",
        backref="parent",
        remote_side=[id]
    )

    def __repr__(self) -> str:
        return f"<TraitCategory {self.name}>"

class LarpTrait(Base):
    """LARP trait model using adjective-based system."""
    __tablename__ = "larp_traits"
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    display_name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String)
    
    # Character relationship
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    character: Mapped["Character"] = relationship("Character", back_populates="larp_traits")
    
    # Categories relationship
    categories: Mapped[List[TraitCategory]] = relationship(
        TraitCategory,
        secondary=trait_categories,
        back_populates="traits"
    )

    def __repr__(self) -> str:
        return f"<LarpTrait {self.name}>"
    
    @property
    def format_display_name(self) -> str:
        """
        Get the name formatted for display.
        
        Returns:
            Formatted trait name
        """
        display = self.name
        if self.is_negative:
            display = f"Negative: {display}"
        if self.is_spent:
            display = f"{display} (Spent)"
        return display 