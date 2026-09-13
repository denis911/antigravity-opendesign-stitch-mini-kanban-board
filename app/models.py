from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class CardModel(BaseModel):
    id: str = Field(default_factory=lambda: f"card_{uuid.uuid4().hex[:8]}")
    column_id: str
    title: str
    description: Optional[str] = ""
    rank: float = 1000.0
    color: str = "default"
    code_id: Optional[str] = None
    tag: Optional[str] = None
    assignee: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ColumnModel(BaseModel):
    id: str
    title: str
    position: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cards: list[CardModel] = Field(default_factory=list)
