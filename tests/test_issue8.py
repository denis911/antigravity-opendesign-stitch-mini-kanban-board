import pytest
from sqlmodel import create_engine
from app.db.session import init_db
from app.repositories.sqlite import SQLiteBoardRepository
from app.services.ranking import calculate_rank, should_rebalance, rebalance_ranks


@pytest.fixture
def sqlite_repo():
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    init_db(test_engine)
    return SQLiteBoardRepository(engine=test_engine)


def test_ranking_math_isolated():
    """Verify ranking calculations across all boundary conditions."""
    # Into empty column
    assert calculate_rank(None, None) == 1000.0

    # At top of column before first card (rank 1000.0)
    assert calculate_rank(None, 1000.0) == 500.0

    # At bottom of column after last card (rank 2000.0)
    assert calculate_rank(2000.0, None) == 3000.0

    # Between Card A (1000.0) and Card B (2000.0)
    assert calculate_rank(1000.0, 2000.0) == 1500.0


def test_ranking_rebalance_trigger():
    """Verify rebalance detection and rank re-spacing."""
    # Distance greater than 1e-6 should not trigger rebalance
    assert not should_rebalance(1000.0, 1000.1)

    # Distance less than 1e-6 should trigger rebalance
    assert should_rebalance(1000.0, 1000.0000001)

    # Rebalancing items
    class DummyCard:
        def __init__(self, rank):
            self.rank = rank

    cards = [DummyCard(1.000001), DummyCard(1.000002), DummyCard(1.000003)]
    rebalanced = rebalance_ranks(cards)
    assert [c.rank for c in rebalanced] == [1000.0, 2000.0, 3000.0]


def test_sqlite_repository_crud(sqlite_repo):
    """Verify all CRUD operations on SQLiteBoardRepository."""
    # list_columns
    cols = sqlite_repo.list_columns()
    assert len(cols) == 4

    # create_card
    new_card = sqlite_repo.create_card(
        column_id="col-backlog",
        title="SQLite Test Card",
        description="Testing SQLite storage",
        color="blue"
    )
    assert new_card.title == "SQLite Test Card"
    assert new_card.color == "blue"
    assert new_card.rank > 0

    # get_card
    retrieved = sqlite_repo.get_card(new_card.id)
    assert retrieved is not None
    assert retrieved.id == new_card.id

    # update_card
    updated = sqlite_repo.update_card(
        card_id=new_card.id,
        title="Renamed Card",
        description="Updated Desc",
        color="green"
    )
    assert updated.title == "Renamed Card"
    assert updated.color == "green"

    # delete_card
    deleted = sqlite_repo.delete_card(new_card.id)
    assert deleted is True
    assert sqlite_repo.get_card(new_card.id) is None


def test_sqlite_repository_move_and_rebalance(sqlite_repo):
    """Verify moving cards across columns and rebalance triggers in SQLite."""
    # Create two cards in col-done
    c1 = sqlite_repo.create_card("col-done", "First Done")
    c2 = sqlite_repo.create_card("col-done", "Second Done")

    # Create a card in col-backlog
    to_move = sqlite_repo.create_card("col-backlog", "Moving Card")

    # Move between c1 and c2 in col-done
    moved = sqlite_repo.move_card(
        card_id=to_move.id,
        target_column_id="col-done",
        prev_card_id=c1.id,
        next_card_id=c2.id
    )
    assert moved.column_id == "col-done"
    assert c1.rank < moved.rank < c2.rank

    # Trigger rebalance with collapsing ranks
    sqlite_repo.update_card(c1.id)  # touch
    with sqlite_repo.engine.connect() as conn:
        pass
