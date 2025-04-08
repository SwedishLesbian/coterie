from typing import List, Optional, Set
from sqlalchemy import String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, Character

# Association table for the many-to-many relationship between traits and categories
trait_category_association = Table(
    "trait_category_association",
    Base.metadata,
    Column("trait_id", ForeignKey("larp_traits.id"), primary_key=True),
    Column("category_id", ForeignKey("trait_categories.id"), primary_key=True)
)

class TraitCategory(Base):
    """Class representing a trait category (Physical, Social, Mental, etc.)."""
    __tablename__ = "trait_categories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    
    # Relationships
    traits: Mapped[List["LarpTrait"]] = relationship(
        "LarpTrait",
        secondary=trait_category_association,
        back_populates="categories"
    )
    
    def __repr__(self) -> str:
        return f"<TraitCategory {self.name}>"

class LarpTrait(Base):
    """
    Class representing an adjective-based LARP trait.
    
    In Mind's Eye Theater, traits are adjectives that describe a character's
    capabilities, rather than numeric values. This class represents a single
    trait adjective that can belong to multiple categories.
    """
    __tablename__ = "larp_traits"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    is_negative: Mapped[bool] = mapped_column(default=False)
    is_temporary: Mapped[bool] = mapped_column(default=False)
    is_custom: Mapped[bool] = mapped_column(default=False)
    is_spent: Mapped[bool] = mapped_column(default=False)
    note: Mapped[Optional[str]] = mapped_column(String)
    
    # Foreign key to character
    character_id: Mapped[int] = mapped_column(ForeignKey("characters.id"))
    
    # Relationships
    character: Mapped["Character"] = relationship(
        "Character", 
        back_populates="larp_traits"
    )
    
    categories: Mapped[List["TraitCategory"]] = relationship(
        "TraitCategory",
        secondary=trait_category_association,
        back_populates="traits"
    )
    
    def __repr__(self) -> str:
        return f"<LarpTrait {self.name}>"
    
    @property
    def display_name(self) -> str:
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