import pytest
from sqlmodel import create_engine, Session, select
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.db.models import Column, Card
from app.db.session import init_db
from app.dependencies import get_repository
from app.repositories.sqlite import SQLiteBoardRepository
from app.services.ranking import calculate_rank, should_rebalance, rebalance_ranks


@pytest.fixture
def memory_db_engine():
    """Isolated in-memory SQLite engine using StaticPool for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    init_db(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def sqlite_repo(memory_db_engine):
    """SQLiteBoardRepository backed by isolated in-memory SQLite."""
    return SQLiteBoardRepository(engine=memory_db_engine)


@pytest.fixture
def test_client(sqlite_repo):
    """FastAPI TestClient with dependency override to the isolated SQLite repo."""
    app.dependency_overrides[get_repository] = lambda: sqlite_repo
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_isolated_sqlite_seeding_and_structure(sqlite_repo):
    """Verify in-memory SQLite initialization and seed structure."""
    cols = sqlite_repo.list_columns()
    assert len(cols) == 4
    col_ids = [c.id for c in cols]
    assert col_ids == ["col-backlog", "col-in-progress", "col-review", "col-done"]

    total_cards = sum(len(c.cards) for c in cols)
    assert total_cards >= 5


def test_cascade_deletion_on_column_delete(memory_db_engine):
    """Verify that deleting a column cascades and removes all associated cards."""
    with Session(memory_db_engine) as session:
        # Verify cards exist in col-backlog
        col = session.exec(select(Column).where(Column.id == "col-backlog")).first()
        assert col is not None
        cards = session.exec(select(Card).where(Card.column_id == "col-backlog")).all()
        assert len(cards) > 0
        card_ids = [c.id for c in cards]

        # Delete column
        session.delete(col)
        session.commit()

        # Check column is gone
        assert session.exec(select(Column).where(Column.id == "col-backlog")).first() is None

        # Check all child cards were deleted by cascade
        remaining_cards = session.exec(select(Card).where(Card.id.in_(card_ids))).all()
        assert len(remaining_cards) == 0


def test_rank_calculation_boundaries(sqlite_repo):
    """Verify all rank calculation boundary conditions."""
    # 1. Empty column insertion
    # Create empty column
    with Session(sqlite_repo.engine) as session:
        new_col = Column(id="col-empty", title="Empty Col", position=10)
        session.add(new_col)
        session.commit()

    card_empty = sqlite_repo.create_card("col-empty", "Card in Empty")
    assert card_empty.rank == 1000.0

    # 2. Bottom of column insertion
    card_second = sqlite_repo.create_card("col-empty", "Second Card")
    assert card_second.rank == 2000.0

    # 3. Top of column insertion (move card to top)
    card_top = sqlite_repo.create_card("col-empty", "Third Card")
    # Move card_top before card_empty (which has rank 1000.0)
    moved_top = sqlite_repo.move_card(
        card_id=card_top.id,
        target_column_id="col-empty",
        prev_card_id=None,
        next_card_id=card_empty.id
    )
    assert moved_top.rank == 500.0  # 1000.0 / 2.0

    # 4. Middle of column insertion (between moved_top:500.0 and card_empty:1000.0)
    card_middle = sqlite_repo.create_card("col-empty", "Fourth Card")
    moved_mid = sqlite_repo.move_card(
        card_id=card_middle.id,
        target_column_id="col-empty",
        prev_card_id=moved_top.id,
        next_card_id=card_empty.id
    )
    assert moved_mid.rank == 750.0  # (500.0 + 1000.0) / 2.0


def test_rebalance_trigger_when_ranks_converge(sqlite_repo):
    """Verify that when adjacent ranks collapse below 1e-6, rebalance re-spaces column ranks."""
    # Seed 2 cards with ranks that will collapse
    with Session(sqlite_repo.engine) as session:
        col = Column(id="col-dense", title="Dense Col", position=20)
        session.add(col)
        c1 = Card(id="dense-1", column_id="col-dense", title="Dense 1", rank=1000.0)
        c2 = Card(id="dense-2", column_id="col-dense", title="Dense 2", rank=1000.0 + 5e-7)
        c3 = Card(id="dense-3", column_id="col-dense", title="Dense 3", rank=3000.0)
        session.add(c1)
        session.add(c2)
        session.add(c3)
        session.commit()

    # Move dense-3 between dense-1 and dense-2
    # The gap between c1 and c2 is 5e-7 (< 1e-6), which triggers rebalance
    moved = sqlite_repo.move_card(
        card_id="dense-3",
        target_column_id="col-dense",
        prev_card_id="dense-1",
        next_card_id="dense-2"
    )

    # After rebalance, cards in col-dense should be re-spaced to [1000.0, 2000.0, 3000.0]
    updated_col = sqlite_repo.get_column("col-dense")
    ranks = [c.rank for c in updated_col.cards]
    assert ranks == [1000.0, 2000.0, 3000.0]


def test_end_to_end_fastapi_sqlite_crud_and_move(test_client, sqlite_repo):
    """Verify full FastAPI hypermedia interactions with SQLite persistence."""
    # 1. GET / renders board
    res = test_client.get("/")
    assert res.status_code == 200
    assert "FastKanban" in res.text

    # 2. POST /cards creates card in SQLite
    res = test_client.post(
        "/cards",
        data={
            "column_id": "col-backlog",
            "title": "E2E SQLite Card",
            "description": "Integration test"
        }
    )
    assert res.status_code == 201
    assert "E2E SQLite Card" in res.text

    # Find created card id
    col = sqlite_repo.get_column("col-backlog")
    created = [c for c in col.cards if c.title == "E2E SQLite Card"][0]

    # 3. PUT /cards/{id} updates card in SQLite
    res = test_client.put(
        f"/cards/{created.id}",
        data={
            "title": "E2E SQLite Card Updated",
            "description": "Integration test updated",
            "color": "green"
        }
    )
    assert res.status_code == 200
    assert "E2E SQLite Card Updated" in res.text

    card_in_db = sqlite_repo.get_card(created.id)
    assert card_in_db.title == "E2E SQLite Card Updated"
    assert card_in_db.color == "green"

    # 4. PATCH /cards/{id}/move moves card to col-done
    res = test_client.patch(
        f"/cards/{created.id}/move",
        data={
            "target_column_id": "col-done",
            "prev_card_id": "",
            "next_card_id": ""
        }
    )
    assert res.status_code == 200

    card_in_db = sqlite_repo.get_card(created.id)
    assert card_in_db.column_id == "col-done"

    # 5. DELETE /cards/{id} deletes card from SQLite
    res = test_client.delete(f"/cards/{created.id}")
    assert res.status_code == 200

    assert sqlite_repo.get_card(created.id) is None
