from typing import Optional
from datetime import datetime, timezone
from app.models import ColumnModel, CardModel
from app.repositories.base import BoardRepository
import uuid


class InMemoryBoardRepository(BoardRepository):
    def __init__(self) -> None:
        self.columns: dict[str, ColumnModel] = {}
        self.cards: dict[str, CardModel] = {}
        self._seed_default_data()

    def _seed_default_data(self) -> None:
        cols = [
            ColumnModel(id="col-backlog", title="Backlog", position=0),
            ColumnModel(id="col-in-progress", title="In Progress", position=1),
            ColumnModel(id="col-review", title="Review", position=2),
            ColumnModel(id="col-done", title="Done", position=3),
        ]
        for col in cols:
            self.columns[col.id] = col

        initial_cards = [
            CardModel(
                id="card-1",
                column_id="col-backlog",
                title="Decouple IndexedDB sync from rendering loop",
                description="Optimize state management by isolating database writes from main UI thread.",
                rank=1000.0,
                color="default",
                code_id="ENG-204",
                tag="perf",
                assignee="KN"
            ),
            CardModel(
                id="card-2",
                column_id="col-backlog",
                title="Evaluate Brotli compression for asset distribution",
                description="Benchmark cold-start bundle sizes against gzip.",
                rank=2000.0,
                color="blue",
                code_id="ENG-209",
                tag="infra",
                assignee="KN"
            ),
            CardModel(
                id="card-3",
                column_id="col-in-progress",
                title="Migrate session token rotation to WebCrypto API",
                description="Replace legacy crypto library with browser-native WebCrypto primitives.",
                rank=1000.0,
                color="yellow",
                code_id="CORE-104",
                tag="auth",
                assignee="TA"
            ),
            CardModel(
                id="card-4",
                column_id="col-review",
                title="Harmonize micro-typography baselines with JetBrains Mono chips",
                description="Align letter-spacing and vertical centering on status tokens.",
                rank=1000.0,
                color="green",
                code_id="ZEN-82",
                tag="ui",
                assignee="SS"
            ),
            CardModel(
                id="card-5",
                column_id="col-done",
                title="Extract organic neutral tokens for Rice Paper palette",
                description="Configure Tailwind theme extension with Washi and Sumi ink colors.",
                rank=1000.0,
                color="default",
                code_id="SYS-12",
                tag="design",
                assignee="YS"
            ),
        ]
        for card in initial_cards:
            self.cards[card.id] = card

    def list_columns(self) -> list[ColumnModel]:
        result = []
        for col in sorted(self.columns.values(), key=lambda c: c.position):
            col_cards = [card for card in self.cards.values() if card.column_id == col.id]
            col_cards.sort(key=lambda c: c.rank)
            result.append(ColumnModel(
                id=col.id,
                title=col.title,
                position=col.position,
                created_at=col.created_at,
                cards=col_cards
            ))
        return result

    def get_column(self, column_id: str) -> Optional[ColumnModel]:
        col = self.columns.get(column_id)
        if not col:
            return None
        col_cards = [c for c in self.cards.values() if c.column_id == column_id]
        col_cards.sort(key=lambda c: c.rank)
        return ColumnModel(
            id=col.id,
            title=col.title,
            position=col.position,
            created_at=col.created_at,
            cards=col_cards
        )

    def get_card(self, card_id: str) -> Optional[CardModel]:
        return self.cards.get(card_id)

    def create_card(
        self,
        column_id: str,
        title: str,
        description: Optional[str] = "",
        color: str = "default",
        tag: Optional[str] = None
    ) -> CardModel:
        col_cards = [c for c in self.cards.values() if c.column_id == column_id]
        max_rank = max([c.rank for c in col_cards], default=0.0)
        new_rank = max_rank + 1000.0 if col_cards else 1000.0

        card = CardModel(
            id=f"card-{uuid.uuid4().hex[:6]}",
            column_id=column_id,
            title=title.strip(),
            description=description.strip() if description else "",
            rank=new_rank,
            color=color,
            code_id=f"KAN-{len(self.cards) + 101}",
            tag=tag or "task"
        )
        self.cards[card.id] = card
        return card

    def update_card(
        self,
        card_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None
    ) -> Optional[CardModel]:
        card = self.cards.get(card_id)
        if not card:
            return None
        if title is not None:
            card.title = title.strip()
        if description is not None:
            card.description = description.strip()
        if color is not None:
            card.color = color
        card.updated_at = datetime.now(timezone.utc)
        return card

    def delete_card(self, card_id: str) -> bool:
        if card_id in self.cards:
            del self.cards[card_id]
            return True
        return False

    def move_card(
        self,
        card_id: str,
        target_column_id: str,
        prev_card_id: Optional[str] = None,
        next_card_id: Optional[str] = None
    ) -> Optional[CardModel]:
        card = self.cards.get(card_id)
        if not card:
            return None

        # Calculate new rank according to spec 3.3
        prev_card = self.cards.get(prev_card_id) if prev_card_id else None
        next_card = self.cards.get(next_card_id) if next_card_id else None

        if prev_card and next_card:
            new_rank = (prev_card.rank + next_card.rank) / 2.0
        elif prev_card and not next_card:
            new_rank = prev_card.rank + 1000.0
        elif not prev_card and next_card:
            new_rank = next_card.rank / 2.0
        else:
            new_rank = 1000.0

        card.column_id = target_column_id
        card.rank = new_rank
        card.updated_at = datetime.now(timezone.utc)
        return card
