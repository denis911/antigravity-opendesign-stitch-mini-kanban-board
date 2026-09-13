import pytest
from sqlmodel import SQLModel, create_engine, Session, select
from app.db.models import Column, Card
from app.db.session import init_db


@pytest.fixture
def sqlite_test_engine():
    # Use in-memory SQLite with foreign keys enabled for test isolation
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    yield test_engine


def test_models_fields():
    """Verify Column and Card models have all fields matching spec section 3.2."""
    col = Column(id="col-test", title="Test Column", position=0)
    assert col.id == "col-test"
    assert col.title == "Test Column"
    assert col.position == 0
    assert col.created_at is not None

    card = Card(
        id="card-test-1",
        column_id="col-test",
        title="Test Card",
        description="A card description",
        rank=1500.0,
        color="red",
        code_id="ENG-101",
        tag="backend"
    )
    assert card.id == "card-test-1"
    assert card.column_id == "col-test"
    assert card.title == "Test Card"
    assert card.description == "A card description"
    assert card.rank == 1500.0
    assert card.color == "red"
    assert card.code_id == "ENG-101"
    assert card.tag == "backend"
    assert card.created_at is not None
    assert card.updated_at is not None


def test_auto_seed_default_columns(sqlite_test_engine):
    """Verify init_db creates tables and auto-seeds default columns."""
    init_db(sqlite_test_engine)

    with Session(sqlite_test_engine) as session:
        cols = session.exec(select(Column).order_by(Column.position)).all()
        assert len(cols) == 4
        col_titles = [c.title for c in cols]
        assert col_titles == ["Backlog", "In Progress", "Review", "Done"]

        cards = session.exec(select(Card)).all()
        assert len(cards) >= 5


def test_cascade_delete(sqlite_test_engine):
    """Verify deleting a column cascades and deletes all its child cards."""
    init_db(sqlite_test_engine)

    with Session(sqlite_test_engine) as session:
        col = session.exec(select(Column).where(Column.id == "col-backlog")).first()
        assert col is not None

        # Check cards belonging to this column exist
        child_cards = session.exec(select(Card).where(Card.column_id == "col-backlog")).all()
        assert len(child_cards) > 0
        child_card_ids = [c.id for c in child_cards]

        # Delete column
        session.delete(col)
        session.commit()

        # Verify child cards were cascade deleted
        remaining_cards = session.exec(select(Card).where(Card.id.in_(child_card_ids))).all()
        assert len(remaining_cards) == 0
