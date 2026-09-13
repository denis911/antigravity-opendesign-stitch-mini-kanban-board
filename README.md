# FastKanban (Zen Minimalist Kanban Board)

A lightweight, full-stack, local-first Kanban board built on the principle of hypermedia-driven architecture using **FastAPI**, **Jinja2**, **HTMX 2.x**, **Tailwind CSS**, and **SortableJS**, styled after the **Stitch Zen Precision ("Kanso Studio")** design system.

---

## Features

- **Zero Node.js Build Pipeline:** Runs directly in modern browsers with plain HTML5, HTMX, and Tailwind CSS.
- **Zen Aesthetics:** Warm washi paper canvas, sumi ink typography, JetBrains Mono tags, and tactile planar depth.
- **Spec-Driven & Phased:** Built incrementally across 3 distinct phases with decoupled repository abstractions.
- **Python Package Management:** Fast, deterministic environment powered exclusively by [`uv`](https://docs.astral.sh/uv/).

---

## Quick Start

### Prerequisites

Ensure [Python 3.11+](https://python.org) and [`uv`](https://docs.astral.sh/uv/) are installed:

```bash
# Verify uv installation
uv --version
```

### 1. Install Dependencies

Sync all project and development dependencies using `uv`:

```bash
uv sync
```

### 2. Run Tests

Execute the automated test suite with `pytest`:

```bash
uv run pytest
```

### 3. Start the Development Server

Launch the FastAPI application with auto-reload:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Open your browser and navigate to:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## Roadmap & Phases

- [x] **Phase 1 (In Progress): Frontend with In-Memory Dummy Backend & Testing**
  - [x] Issue #1: Project scaffold, `uv` environment & repository interface
  - [x] Issue #2: Board layout, columns, and seeded cards rendering (Stitch design)
  - [ ] Issue #3: Inline card creation & deletion with dynamic counter updates
  - [ ] Issue #4: Card edit modal with color tagging
  - [ ] Issue #5: SortableJS drag-and-drop card reordering
  - [ ] Issue #6: Automated testing suite for Phase 1
- [ ] **Phase 2: Persistent Backend Integration (SQLite + SQLModel) & Testing**
  - [ ] Issues #7 – #10: Database engine, float ranking math, persistence across restarts, and integration tests
- [ ] **Phase 3: Local Deployment via Docker Compose**
  - [ ] Issues #11 – #12: Multi-stage Dockerfile with `uv`, volume persistence, and healthchecks

---

## Documentation

- [`_docs/spec.md`](_docs/spec.md) - Full technical specification and API hypermedia contract
- [`_docs/process.md`](_docs/process.md) - Spec-driven development process & roles
- [`_docs/stitch_zen_minimalist_kanban_board/`](_docs/stitch_zen_minimalist_kanban_board/) - Stitch design tokens, colors, and layout reference
