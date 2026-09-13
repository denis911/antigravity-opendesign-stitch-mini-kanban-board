from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_repository

client = TestClient(app)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_in_memory_repository():
    repo = get_repository()
    cols = repo.list_columns()
    assert len(cols) == 4
    col_titles = [c.title for c in cols]
    assert col_titles == ["Backlog", "In Progress", "Review", "Done"]

    total_cards = sum(len(c.cards) for c in cols)
    assert total_cards >= 3
