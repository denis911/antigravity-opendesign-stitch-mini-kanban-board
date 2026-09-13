from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import uuid


class Column(SQLModel, table=True):
    __tablename__ = "columns"

    id: str = Field(primary_key=True, index=True)
    title: str = Field(max_length=100, nullable=False)
    position: int = Field(default=0, nullable=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    cards: List["Card"] = Relationship(
        back_populates="column",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "order_by": "Card.rank"}
    )


class Card(SQLModel, table=True):
    __tablename__ = "cards"

    id: str = Field(
        default_factory=lambda: f"card_{uuid.uuid4().hex[:8]}",
        primary_key=True,
        index=True
    )
    column_id: str = Field(
        foreign_key="columns.id",
        nullable=False,
        index=True,
        ondelete="CASCADE"
    )
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default="", nullable=True)
    rank: float = Field(default=1000.0, nullable=False, index=True)
    color: str = Field(default="default", max_length=20, nullable=False)
    code_id: Optional[str] = Field(default=None, max_length=50, nullable=True)
    tag: Optional[str] = Field(default=None, max_length=50, nullable=True)
    assignee: Optional[str] = Field(default=None, max_length=50, nullable=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    column: Optional[Column] = Relationship(back_populates="cards")
