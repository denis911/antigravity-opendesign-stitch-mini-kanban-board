from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_repository

client = TestClient(app)


def test_board_has_sortable_setup():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    # SortableJS included
    assert "Sortable.min.js" in html
    assert "initKanbanSortables" in html
    assert "kanban-cards-container" in html
    assert 'group: \'kanban-board\'' in html


def test_move_card_across_columns():
    repo = get_repository()
    card = repo.create_card(column_id="col-backlog", title="Card To Move Across")
    initial_backlog = len(repo.get_column("col-backlog").cards)
    initial_done = len(repo.get_column("col-done").cards)

    response = client.patch(
        f"/cards/{card.id}/move",
        data={
            "target_column_id": "col-done",
            "prev_card_id": "",
            "next_card_id": ""
        }
    )
    assert response.status_code == 200
    html = response.text

    # Verify repository updated
    updated_card = repo.get_card(card.id)
    assert updated_card.column_id == "col-done"

    # Counter OOB swaps returned
    new_backlog = len(repo.get_column("col-backlog").cards)
    new_done = len(repo.get_column("col-done").cards)
    assert new_backlog == initial_backlog - 1
    assert new_done == initial_done + 1

    assert f'id="counter-col-backlog"' in html
    assert f'{new_backlog:02d}' in html
    assert f'id="counter-col-done"' in html
    assert f'{new_done:02d}' in html


def test_move_card_within_column_ranking():
    repo = get_repository()
    c1 = repo.create_card(column_id="col-review", title="Review 1")
    c2 = repo.create_card(column_id="col-review", title="Review 2")
    c3 = repo.create_card(column_id="col-review", title="Review 3")

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

    # Verify rank between c1 and c2
    c1_updated = repo.get_card(c1.id)
    c2_updated = repo.get_card(c2.id)
    c3_updated = repo.get_card(c3.id)
    assert c1_updated.rank < c3_updated.rank < c2_updated.rank
    assert c3_updated.rank == (c1_updated.rank + c2_updated.rank) / 2.0


def test_move_card_not_found():
    response = client.patch(
        "/cards/nonexistent-card/move",
        data={
            "target_column_id": "col-done"
        }
    )
    assert response.status_code == 404
