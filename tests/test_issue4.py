from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_repository

client = TestClient(app)


def test_card_has_edit_trigger_attributes():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert 'hx-get="/cards/card-1/edit"' in html
    assert 'hx-target="#modal-container"' in html
    assert 'hx-swap="innerHTML"' in html


def test_get_card_edit_modal():
    response = client.get("/cards/card-1/edit")
    assert response.status_code == 200
    html = response.text

    # Modal structure & Stitch classes
    assert "edit-modal-backdrop" in html
    assert "card-edit-form" in html
    assert 'hx-put="/cards/card-1"' in html
    assert 'hx-target="#card-card-1"' in html
    assert 'hx-swap="outerHTML"' in html

    # Pre-populated fields
    assert "Decouple IndexedDB sync from rendering loop" in html
    assert "Optimize state management" in html

    # Color options
    assert 'value="default"' in html
    assert 'value="red"' in html
    assert 'value="yellow"' in html
    assert 'value="green"' in html
    assert 'value="blue"' in html

    # Action buttons and keyboard Esc listener
    assert "Cancel" in html
    assert "Save Changes" in html
    assert "Escape" in html


def test_get_card_edit_modal_not_found():
    response = client.get("/cards/nonexistent-card-id/edit")
    assert response.status_code == 404


def test_put_card_update_success():
    repo = get_repository()
    card = repo.create_card(column_id="col-backlog", title="Original Title", description="Original Desc")

    response = client.put(
        f"/cards/{card.id}",
        data={
            "title": "Updated Title via Modal",
            "description": "Updated Description text",
            "color": "red"
        }
    )
    assert response.status_code == 200
    html = response.text

    # Updated card HTML returned
    assert "Updated Title via Modal" in html
    assert "Updated Description text" in html
    assert "bg-cinnabar" in html  # Red color dot

    # OOB modal clearance
    assert '<div id="modal-container" hx-swap-oob="innerHTML"></div>' in html

    # Verify repository state
    saved_card = repo.get_card(card.id)
    assert saved_card.title == "Updated Title via Modal"
    assert saved_card.description == "Updated Description text"
    assert saved_card.color == "red"


def test_put_card_update_empty_title_validation():
    repo = get_repository()
    card = repo.create_card(column_id="col-backlog", title="Valid Title")

    response = client.put(
        f"/cards/{card.id}",
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

    # Verify repository was not updated to empty
    saved_card = repo.get_card(card.id)
    assert saved_card.title == "Valid Title"
