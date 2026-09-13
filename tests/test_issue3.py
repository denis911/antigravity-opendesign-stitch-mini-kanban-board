from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_repository

client = TestClient(app)


def test_board_has_add_buttons_and_delete_buttons():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    # Check + Add Card button in columns
    assert "add-card-container-col-backlog" in html
    assert "Add Card" in html
    # Check delete button on cards with confirmation
    assert 'hx-delete="/cards/card-1"' in html
    assert 'hx-confirm="Are you sure you want to delete this card?"' in html


def test_get_card_new_form():
    response = client.get("/cards/new?col_id=col-backlog")
    assert response.status_code == 200
    html = response.text
    assert 'form-add-col-backlog' in html
    assert 'name="title"' in html
    assert 'name="column_id"' in html
    assert 'value="col-backlog"' in html
    assert 'Add' in html
    assert 'Cancel' in html


def test_get_card_cancel_form():
    response = client.get("/cards/cancel-form?col_id=col-backlog")
    assert response.status_code == 200
    html = response.text
    assert "Add Card" in html
    assert 'hx-get="/cards/new?col_id=col-backlog"' in html


def test_create_card_success():
    repo = get_repository()
    initial_col = repo.get_column("col-backlog")
    initial_count = len(initial_col.cards)

    response = client.post(
        "/cards",
        data={
            "column_id": "col-backlog",
            "title": "New Spec-Driven Feature",
            "description": "Details about the feature"
        }
    )
    assert response.status_code == 201
    html = response.text

    # Appended card fragment
    assert "New Spec-Driven Feature" in html
    assert "Details about the feature" in html
    assert "kanban-card" in html

    # OOB counter updated
    new_col = repo.get_column("col-backlog")
    new_count = len(new_col.cards)
    assert new_count == initial_count + 1
    assert f'id="counter-col-backlog"' in html
    assert f'{new_count:02d}' in html

    # OOB add-button restored
    assert 'id="add-card-container-col-backlog"' in html


def test_create_card_empty_title_validation():
    repo = get_repository()
    initial_col = repo.get_column("col-backlog")
    initial_count = len(initial_col.cards)

    response = client.post(
        "/cards",
        data={
            "column_id": "col-backlog",
            "title": "   ",
            "description": ""
        }
    )
    assert response.status_code == 200
    html = response.text
    assert "Title cannot be empty" in html
    assert response.headers.get("hx-retarget") == "#add-card-container-col-backlog"

    # Verify no card was created
    new_col = repo.get_column("col-backlog")
    assert len(new_col.cards) == initial_count


def test_delete_card_success():
    repo = get_repository()
    # Create card to delete
    card = repo.create_card(column_id="col-in-progress", title="Card to delete")
    initial_col = repo.get_column("col-in-progress")
    initial_count = len(initial_col.cards)

    response = client.delete(f"/cards/{card.id}")
    assert response.status_code == 200
    html = response.text

    # Verify repository removed card
    assert repo.get_card(card.id) is None
    new_col = repo.get_column("col-in-progress")
    assert len(new_col.cards) == initial_count - 1

    # Counter updated via OOB swap
    assert f'id="counter-col-in-progress"' in html
    assert f'{initial_count - 1:02d}' in html
