from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Session, select
from sqlalchemy.engine import Engine
from app.models import ColumnModel, CardModel
from app.repositories.base import BoardRepository
from app.db.models import Column, Card
from app.db.session import engine as default_engine
from app.services.ranking import calculate_rank, should_rebalance, rebalance_ranks
import uuid


class SQLiteBoardRepository(BoardRepository):
    def __init__(self, engine: Engine = default_engine) -> None:
        self.engine = engine

    def _to_card_model(self, card: Card) -> CardModel:
        return CardModel(
            id=card.id,
            column_id=card.column_id,
            title=card.title,
            description=card.description,
            rank=card.rank,
            color=card.color,
            code_id=card.code_id,
            tag=card.tag,
            assignee=card.assignee,
            created_at=card.created_at,
            updated_at=card.updated_at,
        )

    def _to_column_model(self, col: Column, cards: list[Card]) -> ColumnModel:
        sorted_cards = sorted(cards, key=lambda c: c.rank)
        return ColumnModel(
            id=col.id,
            title=col.title,
            position=col.position,
            created_at=col.created_at,
            cards=[self._to_card_model(c) for c in sorted_cards]
        )

    def list_columns(self) -> list[ColumnModel]:
        with Session(self.engine) as session:
            cols = session.exec(select(Column).order_by(Column.position)).all()
            all_cards = session.exec(select(Card)).all()
            cards_by_col: dict[str, list[Card]] = {}
            for c in all_cards:
                cards_by_col.setdefault(c.column_id, []).append(c)

            return [self._to_column_model(col, cards_by_col.get(col.id, [])) for col in cols]

    def get_column(self, column_id: str) -> Optional[ColumnModel]:
        with Session(self.engine) as session:
            col = session.exec(select(Column).where(Column.id == column_id)).first()
            if not col:
                return None
            cards = session.exec(select(Card).where(Card.column_id == column_id)).all()
            return self._to_column_model(col, list(cards))

    def get_card(self, card_id: str) -> Optional[CardModel]:
        with Session(self.engine) as session:
            card = session.exec(select(Card).where(Card.id == card_id)).first()
            return self._to_card_model(card) if card else None

    def create_card(
        self,
        column_id: str,
        title: str,
        description: Optional[str] = "",
        color: str = "default",
        tag: Optional[str] = None
    ) -> CardModel:
        with Session(self.engine) as session:
            col_cards = session.exec(
                select(Card).where(Card.column_id == column_id).order_by(Card.rank.desc())
            ).all()
            max_rank = col_cards[0].rank if col_cards else 0.0
            new_rank = max_rank + 1000.0 if col_cards else 1000.0

            card = Card(
                id=f"card-{uuid.uuid4().hex[:6]}",
                column_id=column_id,
                title=title.strip(),
                description=description.strip() if description else "",
                rank=new_rank,
                color=color,
                code_id=f"KAN-{len(session.exec(select(Card)).all()) + 101}",
                tag=tag or "task",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(card)
            session.commit()
            session.refresh(card)
            return self._to_card_model(card)

    def update_card(
        self,
        card_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None
    ) -> Optional[CardModel]:
        with Session(self.engine) as session:
            card = session.exec(select(Card).where(Card.id == card_id)).first()
            if not card:
                return None
            if title is not None:
                card.title = title.strip()
            if description is not None:
                card.description = description.strip()
            if color is not None:
                card.color = color
            card.updated_at = datetime.now(timezone.utc)
            session.add(card)
            session.commit()
            session.refresh(card)
            return self._to_card_model(card)

    def delete_card(self, card_id: str) -> bool:
        with Session(self.engine) as session:
            card = session.exec(select(Card).where(Card.id == card_id)).first()
            if not card:
                return False
            session.delete(card)
            session.commit()
            return True

    def move_card(
        self,
        card_id: str,
        target_column_id: str,
        prev_card_id: Optional[str] = None,
        next_card_id: Optional[str] = None
    ) -> Optional[CardModel]:
        with Session(self.engine) as session:
            card = session.exec(select(Card).where(Card.id == card_id)).first()
            if not card:
                return None

            prev_card = session.exec(select(Card).where(Card.id == prev_card_id)).first() if prev_card_id else None
            next_card = session.exec(select(Card).where(Card.id == next_card_id)).first() if next_card_id else None

            prev_rank = prev_card.rank if prev_card else None
            next_rank = next_card.rank if next_card else None

            new_rank = calculate_rank(prev_rank, next_rank)

            card.column_id = target_column_id
            card.rank = new_rank
            card.updated_at = datetime.now(timezone.utc)
            session.add(card)
            session.commit()

            # Check if precision requires rebalancing
            if should_rebalance(prev_rank, next_rank):
                target_cards = session.exec(
                    select(Card).where(Card.column_id == target_column_id).order_by(Card.rank)
                ).all()
                rebalanced = rebalance_ranks(list(target_cards))
                for c in rebalanced:
                    session.add(c)
                session.commit()

            session.refresh(card)
            return self._to_card_model(card)
