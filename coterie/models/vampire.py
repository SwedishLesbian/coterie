from typing import Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Character, Trait

class Vampire(Character):
    """Vampire: The Masquerade character class."""
    __tablename__ = "vampires"
    
    id: Mapped[int] = mapped_column(ForeignKey("characters.id"), primary_key=True)
    
    # Vampire-specific attributes
    clan: Mapped[str] = mapped_column(String(50))
    sect: Mapped[str] = mapped_column(String(50))
    generation: Mapped[int] = mapped_column(Integer)
    title: Mapped[Optional[str]] = mapped_column(String(100))
    coterie: Mapped[Optional[str]] = mapped_column(String(100))
    sire: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Path of Enlightenment
    path: Mapped[str] = mapped_column(String(100), default="Humanity")
    path_traits: Mapped[int] = mapped_column(Integer, default=0)
    temp_path_traits: Mapped[int] = mapped_column(Integer, default=0)
    
    # Virtues
    conscience: Mapped[int] = mapped_column(Integer, default=0)
    temp_conscience: Mapped[int] = mapped_column(Integer, default=0)
    self_control: Mapped[int] = mapped_column(Integer, default=0)
    temp_self_control: Mapped[int] = mapped_column(Integer, default=0)
    courage: Mapped[int] = mapped_column(Integer, default=0)
    temp_courage: Mapped[int] = mapped_column(Integer, default=0)
    
    # Blood Pool
    blood: Mapped[int] = mapped_column(Integer, default=0)
    temp_blood: Mapped[int] = mapped_column(Integer, default=0)
    
    # Aura
    aura: Mapped[Optional[str]] = mapped_column(String(50))
    aura_bonus: Mapped[Optional[str]] = mapped_column(String(50))
    
    __mapper_args__ = {
        "polymorphic_identity": "vampire",
    }

class Discipline(Trait):
    """Vampire disciplines."""
    __tablename__ = "disciplines"
    
    id: Mapped[int] = mapped_column(ForeignKey("traits.id"), primary_key=True)
    path: Mapped[Optional[str]] = mapped_column(String(100))  # For Thaumaturgy/Necromancy paths
    
    __mapper_args__ = {
        "polymorphic_identity": "discipline",
    }

class Ritual(Trait):
    """Vampire rituals (Thaumaturgy/Necromancy)."""
    __tablename__ = "rituals"
    
    id: Mapped[int] = mapped_column(ForeignKey("traits.id"), primary_key=True)
    level: Mapped[int] = mapped_column(Integer)
    path: Mapped[str] = mapped_column(String(100))
    
    __mapper_args__ = {
        "polymorphic_identity": "ritual",
    }

class Bond(Trait):
    """Blood bonds."""
    __tablename__ = "bonds"
    
    id: Mapped[int] = mapped_column(ForeignKey("traits.id"), primary_key=True)
    bondee: Mapped[str] = mapped_column(String(100))  # Who is bound
    bonder: Mapped[str] = mapped_column(String(100))  # Who created the bond
    
    __mapper_args__ = {
        "polymorphic_identity": "bond",
    } 