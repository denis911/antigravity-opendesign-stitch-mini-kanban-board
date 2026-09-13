from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_board_html():
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    # Header and branding
    assert "FastKanban" in html
    assert "Sprint 34" in html

    # 4 columns from Stitch design
    assert "Backlog" in html
    assert "In Progress" in html
    assert "Review" in html
    assert "Done" in html

    # Seeded cards
    assert "Decouple IndexedDB sync" in html
    assert "Migrate session token rotation" in html
    assert "Harmonize micro-typography" in html
    assert "Extract organic neutral tokens" in html

    # Tailwind & fonts inclusion
    assert "tailwindcss" in html
    assert "font-mono" in html
    assert "surface-container" in html
