from typing import List, Optional, Dict
from sqlalchemy import String, ForeignKey, Table, Column, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

# Association table for menu items and their submenus
menu_submenu_association = Table(
    "menu_submenu_association",
    Base.metadata,
    Column("parent_id", ForeignKey("menu_items.id"), primary_key=True),
    Column("child_id", ForeignKey("menu_items.id"), primary_key=True)
)

class MenuItem(Base):
    """
    Class representing a menu item from Grapevine menu files.
    
    Menu items can be traits, powers, backgrounds, etc. They can have costs,
    notes, and can include other menu items (submenus).
    """
    __tablename__ = "menu_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    cost: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("menu_categories.id"), nullable=True)
    
    # Relationships
    category: Mapped[Optional["MenuCategory"]] = relationship("MenuCategory", back_populates="items")
    parent_menus: Mapped[List["MenuItem"]] = relationship(
        "MenuItem",
        secondary=menu_submenu_association,
        primaryjoin=id==menu_submenu_association.c.child_id,
        secondaryjoin=id==menu_submenu_association.c.parent_id,
        back_populates="submenus"
    )
    submenus: Mapped[List["MenuItem"]] = relationship(
        "MenuItem",
        secondary=menu_submenu_association,
        primaryjoin=id==menu_submenu_association.c.parent_id,
        secondaryjoin=id==menu_submenu_association.c.child_id,
        back_populates="parent_menus"
    )
    
    def __repr__(self) -> str:
        return f"<MenuItem {self.name}>"

class MenuCategory(Base):
    """
    Class representing a menu category from Grapevine menu files.
    
    Categories group related menu items and can have display settings
    and requirements.
    """
    __tablename__ = "menu_categories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    display_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    alphabetical: Mapped[bool] = mapped_column(Boolean, default=True)
    required: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    items: Mapped[List["MenuItem"]] = relationship("MenuItem", back_populates="category")
    
    def __repr__(self) -> str:
        return f"<MenuCategory {self.name}>" 