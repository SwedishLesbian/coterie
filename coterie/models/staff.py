"""Staff member model for Coterie."""
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .chronicle import Chronicle

class Staff(Base):
    """Staff member model for Coterie."""
    __tablename__ = 'staff'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    chronicle_id: Mapped[int] = mapped_column(Integer, ForeignKey('chronicles.id'))

    # Relationship
    chronicle: Mapped["Chronicle"] = relationship(back_populates="staff")

    def __repr__(self) -> str:
        return f"<Staff(name='{self.name}', role='{self.role}')>" 