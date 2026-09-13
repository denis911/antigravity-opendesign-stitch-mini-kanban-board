# FastKanban (Zen Minimalist Kanban Board)

A lightweight, full-stack, local-first Kanban board built on the principle of hypermedia-driven architecture using **FastAPI**, **Jinja2**, **HTMX 2.x**, **Tailwind CSS**, and **SortableJS**, styled after the **Stitch Zen Precision ("Kanso Studio")** design system.

---

## Features

- **Zero Node.js Build Pipeline:** Runs directly in modern browsers with plain HTML5, HTMX, and Tailwind CSS.
- **Zen Aesthetics:** Warm washi paper canvas (`#faf9f5`), sumi ink typography, JetBrains Mono tags, and tactile planar depth.
- **Spec-Driven & Phased:** Built incrementally across 3 distinct phases with decoupled repository abstractions.
- **Python Package Management:** Fast, deterministic environment powered exclusively by [`uv`](https://docs.astral.sh/uv/).
- **Containerized Durability:** Multi-stage Docker image with non-root security and volume-backed SQLite persistence.

---

## Quick Start

### Prerequisites

Ensure [Python 3.11+](https://python.org) and [`uv`](https://docs.astral.sh/uv/) (or Docker) are installed:

```bash
uv --version
```

### 1. Local Development

Sync dependencies and start the local development server:

```bash
# Sync dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload --port 8000
```

Open your browser at: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

### 2. Run Tests

Run the complete automated test suite (43 tests, 100% pass rate):

```bash
uv run pytest
```

### 3. Docker Compose Deployment

Build and run via Docker Compose with volume-backed persistence:

```bash
# Launch container in background
docker compose up --build -d

# Check health status
docker compose ps

# Follow logs
docker compose logs -f

# Stop container
docker compose down
```

### 4. Convenience Runner (`manage.py` & `Makefile`)

Cross-platform helper commands are available via `python manage.py` (or `make`):

| Task | Python Script | Makefile |
| :--- | :--- | :--- |
| Run Dev Server | `python manage.py dev` | `make dev` |
| Run Tests | `python manage.py test` | `make test` |
| Sync Dependencies | `python manage.py sync` | `make sync` |
| Docker Up | `python manage.py up` | `make up` |
| Docker Down | `python manage.py down` | `make down` |
| Container Status | `python manage.py status` | `make status` |
| Stream Logs | `python manage.py logs` | `make logs` |

---

## Roadmap & Phases

- [x] **Phase 1: Frontend with In-Memory Dummy Backend & Testing (Completed)**
  - [x] Issue #1: Project scaffold, `uv` environment & repository interface
  - [x] Issue #2: Board layout, columns, and seeded cards rendering (Stitch design)
  - [x] Issue #3: Inline card creation & deletion with dynamic counter updates
  - [x] Issue #4: Card edit modal with color tagging
  - [x] Issue #5: SortableJS drag-and-drop card reordering
  - [x] Issue #6: Automated testing suite for Phase 1
- [x] **Phase 2: Persistent Backend Integration (SQLite + SQLModel) & Testing (Completed)**
  - [x] Issue #7: SQLModel entities, SQLite database engine & auto-seeding
  - [x] Issue #8: SQLiteBoardRepository & float ranking engine with rebalancing
  - [x] Issue #9: Connect FastAPI routes to SQLite repository & verify persistence
  - [x] Issue #10: Automated integration & persistence test suite
- [x] **Phase 3: Local Deployment via Docker Compose (Completed)**
  - [x] Issue #11: Multi-stage Dockerfile with `uv` and docker-compose.yml
  - [x] Issue #12: Healthchecks, dev scripts & deployment verification

---

## Documentation

- [`_docs/spec.md`](_docs/spec.md) - Full technical specification and API hypermedia contract
- [`_docs/process.md`](_docs/process.md) - Spec-driven development process & roles
- [`_docs/stitch_zen_minimalist_kanban_board/`](_docs/stitch_zen_minimalist_kanban_board/) - Stitch design tokens, colors, and layout reference
