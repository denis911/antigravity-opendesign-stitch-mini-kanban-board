import os
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from sqlmodel import create_engine
from app.main import app
from app.dependencies import get_repository
from app.repositories.sqlite import SQLiteBoardRepository
from app.db.session import init_db

client = TestClient(app)


def test_default_dependency_is_sqlite():
    """FastAPI get_repository provides SQLiteBoardRepository by default."""
    repo = get_repository()
    assert isinstance(repo, SQLiteBoardRepository)


def test_sqlite_persistence_across_reconnects():
    """Verify that cards added, edited, and moved persist in the SQLite DB across sessions."""
    # Use a real temporary file-based SQLite database
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test_kanban.db"
        db_url = f"sqlite:///{db_file}"

        # 1. Initialize DB and create repo
        engine_1 = create_engine(db_url, echo=False)
        init_db(engine_1)
        repo_1 = SQLiteBoardRepository(engine=engine_1)

        # Wire dependency override for client
        app.dependency_overrides[get_repository] = lambda: repo_1

        # 2. Add a card via HTTP POST /cards
        post_res = client.post(
            "/cards",
            data={
                "column_id": "col-backlog",
                "title": "Persistent Feature",
                "description": "Must survive restarts"
            }
        )
        assert post_res.status_code == 201

        # 3. Modify details via HTTP PUT /cards/{id}
        cards = [c for c in repo_1.list_columns() if c.id == "col-backlog"][0].cards
        persistent_card = [c for c in cards if c.title == "Persistent Feature"][0]

        put_res = client.put(
            f"/cards/{persistent_card.id}",
            data={
                "title": "Renamed Persistent Feature",
                "description": "Updated context",
                "color": "yellow"
            }
        )
        assert put_res.status_code == 200

        # 4. Move card to col-done via HTTP PATCH /cards/{id}/move
        patch_res = client.patch(
            f"/cards/{persistent_card.id}/move",
            data={
                "target_column_id": "col-done",
                "prev_card_id": "",
                "next_card_id": ""
            }
        )
        assert patch_res.status_code == 200

        # Disconnect engine_1 (simulating server shutdown)
        engine_1.dispose()
        app.dependency_overrides.clear()

        # 5. Connect fresh engine_2 to the same database file (simulating server restart)
        engine_2 = create_engine(db_url, echo=False)
        repo_2 = SQLiteBoardRepository(engine=engine_2)
        app.dependency_overrides[get_repository] = lambda: repo_2

        # 6. Verify GET / loads the persisted state from disk
        get_res = client.get("/")
        assert get_res.status_code == 200
        html = get_res.text
        assert "Renamed Persistent Feature" in html

        # Verify card is in col-done with yellow color in repo_2
        done_col = repo_2.get_column("col-done")
        done_card = [c for c in done_col.cards if c.id == persistent_card.id][0]
        assert done_card.title == "Renamed Persistent Feature"
        assert done_card.color == "yellow"
        assert done_card.description == "Updated context"

        # Cleanup
        engine_2.dispose()
        app.dependency_overrides.clear()
