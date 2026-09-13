from typing import Protocol, Optional
from app.models import ColumnModel, CardModel


class BoardRepository(Protocol):
    def list_columns(self) -> list[ColumnModel]:
        """List all columns ordered by position, including their cards ordered by rank."""
        ...

    def get_column(self, column_id: str) -> Optional[ColumnModel]:
        """Retrieve a specific column by ID."""
        ...

    def get_card(self, card_id: str) -> Optional[CardModel]:
        """Retrieve a specific card by ID."""
        ...

    def create_card(
        self,
        column_id: str,
        title: str,
        description: Optional[str] = "",
        color: str = "default",
        tag: Optional[str] = None
    ) -> CardModel:
        """Create a new card placed at the bottom of the specified column."""
        ...

    def update_card(
        self,
        card_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None
    ) -> Optional[CardModel]:
        """Update fields of an existing card."""
        ...

    def delete_card(self, card_id: str) -> bool:
        """Delete a card by ID. Returns True if deleted, False if not found."""
        ...

    def move_card(
        self,
        card_id: str,
        target_column_id: str,
        prev_card_id: Optional[str] = None,
        next_card_id: Optional[str] = None
    ) -> Optional[CardModel]:
        """Move card to a new position/column and recalculate float rank."""
        ...
