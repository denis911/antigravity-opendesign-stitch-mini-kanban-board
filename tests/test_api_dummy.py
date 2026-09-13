import pytest
from fastapi.testclient import TestClient
from app.main import app as fastapi_app
from app.dependencies import get_repository
from app.repositories.memory import InMemoryBoardRepository
import app.dependencies as deps

client = TestClient(fastapi_app)


@pytest.fixture(autouse=True)
def fresh_repo(monkeypatch):
    """Ensure tests run against a fresh or predictable in-memory repository state."""
    mem_repo = InMemoryBoardRepository()
    monkeypatch.setenv("REPO_TYPE", "memory")
    monkeypatch.setattr(deps, "_in_memory_repo", mem_repo)
    fastapi_app.dependency_overrides[get_repository] = lambda: mem_repo
    yield mem_repo
    fastapi_app.dependency_overrides.pop(get_repository, None)


def test_healthz_endpoint():
    """GET /healthz returns status ok."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_board_layout_contains_all_columns():
    """GET / renders board page with all 4 default column titles."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    assert "FastKanban" in html
    assert "Backlog" in html
    assert "In Progress" in html
    assert "Review" in html
    assert "Done" in html

    # Initial seeded cards are visible
    assert "Decouple IndexedDB sync" in html
    assert "Migrate session token rotation" in html


def test_post_cards_success():
    """POST /cards creates card and returns card fragment with OOB counter update."""
    repo = get_repository()
    initial_count = len(repo.get_column("col-backlog").cards)

    response = client.post(
        "/cards",
        data={
            "column_id": "col-backlog",
            "title": "Automated Test Card",
            "description": "Created during dummy API testing"
        }
    )
    assert response.status_code == 201
    html = response.text

    # Card fragment rendered
    assert "Automated Test Card" in html
    assert "Created during dummy API testing" in html
    assert "kanban-card" in html

    # Out-of-band counter updated
    new_count = initial_count + 1
    assert 'id="counter-col-backlog"' in html
    assert f"{new_count:02d}" in html

    # Out-of-band add button restored
    assert 'id="add-card-container-col-backlog"' in html


def test_post_cards_empty_title_validation():
    """POST /cards with empty title returns form with validation error."""
    repo = get_repository()
    initial_count = len(repo.get_column("col-backlog").cards)

    response = client.post(
        "/cards",
        data={
            "column_id": "col-backlog",
            "title": "   ",
            "description": "Empty title task"
        }
    )
    assert response.status_code == 200
    html = response.text

    assert "Title cannot be empty" in html
    assert response.headers.get("hx-retarget") == "#add-card-container-col-backlog"

    # Verify no card was added
    assert len(repo.get_column("col-backlog").cards) == initial_count


def test_get_card_edit_modal():
    """GET /cards/{id}/edit returns modal_edit.html fragment."""
    response = client.get("/cards/card-1/edit")
    assert response.status_code == 200
    html = response.text

    assert "edit-modal-backdrop" in html
    assert "card-edit-form" in html
    assert 'hx-put="/cards/card-1"' in html
    assert "Decouple IndexedDB sync from rendering loop" in html
    assert "Save Changes" in html


def test_get_card_edit_modal_not_found():
    """GET /cards/{id}/edit returns 404 for unknown card."""
    response = client.get("/cards/non-existent-card-id/edit")
    assert response.status_code == 404


def test_put_card_update_success():
    """PUT /cards/{id} updates card fields and closes modal via OOB."""
    response = client.put(
        "/cards/card-1",
        data={
            "title": "Updated Task Title",
            "description": "Updated Task Description",
            "color": "yellow"
        }
    )
    assert response.status_code == 200
    html = response.text

    # Updated card HTML returned
    assert "Updated Task Title" in html
    assert "Updated Task Description" in html
    assert "bg-amber-raw" in html  # Yellow priority dot

    # Modal container cleared via OOB
    assert '<div id="modal-container" hx-swap-oob="innerHTML"></div>' in html

    # Verify repository state
    repo = get_repository()
    card = repo.get_card("card-1")
    assert card.title == "Updated Task Title"
    assert card.description == "Updated Task Description"
    assert card.color == "yellow"


def test_put_card_update_empty_title_validation():
    """PUT /cards/{id} with empty title rejects update with validation message."""
    response = client.put(
        "/cards/card-1",
        data={
            "title": "   ",
            "description": "Some description",
            "color": "default"
        }
    )
    assert response.status_code == 200
    html = response.text

    assert "Title cannot be empty" in html
    assert response.headers.get("hx-retarget") == "#modal-container"

    repo = get_repository()
    card = repo.get_card("card-1")
    assert card.title != ""  # Original title preserved


def test_delete_card_success():
    """DELETE /cards/{id} removes card and decrements column counter OOB."""
    repo = get_repository()
    initial_count = len(repo.get_column("col-in-progress").cards)

    response = client.delete("/cards/card-3")
    assert response.status_code == 200
    html = response.text

    assert repo.get_card("card-3") is None
    new_count = len(repo.get_column("col-in-progress").cards)
    assert new_count == initial_count - 1

    # Counter OOB updated
    assert 'id="counter-col-in-progress"' in html
    assert f"{new_count:02d}" in html


def test_patch_move_card_across_columns():
    """PATCH /cards/{id}/move moves card between columns and updates both counters."""
    repo = get_repository()
    from_initial = len(repo.get_column("col-backlog").cards)
    to_initial = len(repo.get_column("col-done").cards)

    response = client.patch(
        "/cards/card-1/move",
        data={
            "target_column_id": "col-done",
            "prev_card_id": "",
            "next_card_id": ""
        }
    )
    assert response.status_code == 200
    html = response.text

    card = repo.get_card("card-1")
    assert card.column_id == "col-done"

    # Both counters updated via OOB
    from_new = len(repo.get_column("col-backlog").cards)
    to_new = len(repo.get_column("col-done").cards)
    assert from_new == from_initial - 1
    assert to_new == to_initial + 1

    assert f'id="counter-col-backlog"' in html
    assert f"{from_new:02d}" in html
    assert f'id="counter-col-done"' in html
    assert f"{to_new:02d}" in html


def test_patch_move_card_within_column_ranking():
    """PATCH /cards/{id}/move calculates float rank when moving between sibling cards."""
    repo = get_repository()
    # Add 3 cards to col-review
    c1 = repo.create_card("col-review", "Card Alpha")
    c2 = repo.create_card("col-review", "Card Beta")
    c3 = repo.create_card("col-review", "Card Gamma")

    # Move c3 between c1 and c2
    response = client.patch(
        f"/cards/{c3.id}/move",
        data={
            "target_column_id": "col-review",
            "prev_card_id": c1.id,
            "next_card_id": c2.id
        }
    )
    assert response.status_code == 200

    c1_updated = repo.get_card(c1.id)
    c2_updated = repo.get_card(c2.id)
    c3_updated = repo.get_card(c3.id)

    assert c1_updated.rank < c3_updated.rank < c2_updated.rank
    assert c3_updated.rank == (c1_updated.rank + c2_updated.rank) / 2.0
