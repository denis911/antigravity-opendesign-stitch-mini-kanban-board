# Project Specification: FastKanban (HTMX + FastAPI)

## 1. Overview & Problem Statement

Modern Kanban applications frequently suffer from excessive client-side bloat, vendor lock-in, and fragile build chains.

**FastKanban** is a lightweight, full-stack, local-first Kanban board built on the principle of hypermedia-driven architecture. It provides an intuitive, friction-free task management experience using server-rendered HTML fragments and declarative UI interactions, eliminating client-side state managers and Node-based compilation pipelines.

### 1.1 Goals

* **Zero-build frontend:** Runs directly in modern browsers using plain HTML5, HTMX, Tailwind CSS (via CDN or standalone CLI), and SortableJS.
* **Deterministic, predictable backend:** FastAPI service utilizing Python 3.11+ managed via `uv` and `uv run`.
* **Phased spec-driven implementation:**
  * **Phase 1:** Frontend UI with in-memory Dummy Backend (testing interactions, styling, drag-and-drop, modals).
  * **Phase 2:** Persistent SQLite Backend via SQLModel/SQLAlchemy (testing transactions, float ranking, rebalancing).
  * **Phase 3:** Local deployment via Docker Compose with volume-mounted persistence.
* **Modular Storage Abstraction:** A repository interface allows swapping between in-memory mock storage (Phase 1) and SQLite persistence (Phase 2) without rewriting route handlers.

### 1.2 Non-Goals

* Multi-tenant authentication and team permission matrices (Single-user / team-shared board scope for MVP).
* Complex rich-text WYSIWYG editing inside cards (Plaintext and simple Markdown only).
* WebSocket streaming (HTMX polling or standard HTTP swaps suffice for single-user interactions).

---

## 2. Architecture & Tech Stack

```
[ Browser Client ]
  │
  ├─ HTMX 2.x (AJAX swaps, trigger handling)
  ├─ SortableJS (Drag-and-drop event dispatching)
  └─ Tailwind CSS (Styling via CDN utility classes)
        │
        ▼ HTTP (HTML Fragments & JSON)
[ FastAPI Backend ]
  │
  ├─ Jinja2Templates (Server-rendered components/fragments)
  ├─ Pydantic v2 (Input validation & schemas)
  ├─ Repository Protocol (Storage Interface)
        │
        ├── Phase 1: InMemoryBoardRepository (Dummy Backend)
        └── Phase 2: SQLiteBoardRepository (SQLModel / SQLAlchemy)
              │
              ▼
        [ SQLite Engine ] (Mounted file: `kanban.db`)
```

### 2.1 Technology Choices & Tooling

* **Package & Task Runner:** `uv` (`uv add`, `uv run uvicorn ...`, `uv run pytest`).
* **Frontend:** HTMX (`v2.0.x`), Tailwind CSS (`v3.x` CDN), SortableJS (`v1.15.x`).
* **Backend:** Python 3.11+, FastAPI (`>=0.110`), Uvicorn, Jinja2.
* **Persistence (Phase 2):** SQLite with Write-Ahead Logging (WAL) enabled; SQLModel/SQLAlchemy for typed models and queries.
* **Containerization (Phase 3):** Multi-stage `Dockerfile` based on `python` with `astral-sh/uv` binary and `docker-compose.yml`.

---

## 3. Data Model & Storage

### 3.1 ER Diagram

```
┌──────────────────┐       1:N       ┌──────────────────┐
│     columns      │────────────────▶│      cards       │
├──────────────────┤                 ├──────────────────┤
│ id (TEXT/PK)     │                 │ id (TEXT/PK)     │
│ title (TEXT)     │                 │ column_id (FK)   │
│ position (INT)   │                 │ title (TEXT)     │
│ created_at (DATETIME)              │ description(TEXT)│
└──────────────────┘                 │ rank (REAL)      │
                                     │ color (TEXT)     │
                                     │ created_at (DATETIME)
                                     │ updated_at (DATETIME)
                                     └──────────────────┘
```

### 3.2 Field Definitions

#### Columns (`columns`)

* `id`: `TEXT` (Primary Key, e.g., `todo`, `in-progress`, `review`, `done`).
* `title`: `VARCHAR(100)`, Not Null.
* `position`: `INTEGER`, Not Null (0-indexed sequence of columns across the board).
* `created_at`: `DATETIME`, Default UTC current timestamp.

#### Cards (`cards`)

* `id`: `TEXT` (Primary Key, e.g. UUIDv4 or `card_xxxx`).
* `column_id`: `TEXT`, Foreign Key references `columns(id)` on delete cascade.
* `title`: `VARCHAR(255)`, Not Null.
* `description`: `TEXT`, Nullable.
* `rank`: `REAL`, Not Null (Floating-point rank for $O(1)$ reordering without cascading updates).
* `color`: `VARCHAR(20)`, Default `'default'` (Supports visual priority tags: `default`, `red`, `yellow`, `green`, `blue`).
* `created_at`: `DATETIME`, Default UTC current timestamp.
* `updated_at`: `DATETIME`, Default UTC current timestamp.

### 3.3 Float Ranking Strategy for Drag & Drop

To reorder cards without rewriting the indices of all subsequent rows:

* When inserting between `Card A` (rank $R_A$) and `Card B` (rank $R_B$):

$$\text{New Rank} = \frac{R_A + R_B}{2}$$

* Moving to the top of a column (before first card with rank $R_{\text{first}}$):

$$\text{New Rank} = \frac{R_{\text{first}}}{2}$$

* Moving to the bottom of a column (after last card with rank $R_{\text{last}}$):

$$\text{New Rank} = R_{\text{last}} + 1000.0$$

* Empty column initial placement:

$$\text{New Rank} = 1000.0$$

* Rebalance trigger: If $|R_A - R_B| < 1e-6$, column ranks are re-spaced to $[1000.0, 2000.0, 3000.0...]$.

---

## 4. User Stories & Acceptance Criteria

### US-1: View Board and Columns
* **As a** user,
* **I want to** load the main page and view all default columns (*Backlog*, *In Progress*, *Review*, *Done*) with their cards,
* **So that** I have immediate visibility over active work.
* **Acceptance Criteria:**
  - Page loads with a standard 4-column responsive layout.
  - Each column displays its title, dynamic card counter pill, and card list container.
  - Empty columns render a subtle placeholder drop zone.

### US-2: Create a New Card
* **As a** user,
* **I want to** add a new card to any column using an inline form,
* **So that** I can capture tasks quickly.
* **Acceptance Criteria:**
  - Each column footer has an `+ Add Card` button.
  - Clicking displays an inline form (Title input, Add and Cancel buttons).
  - Submitting via `Enter` or clicking `Add` sends an HTMX request that appends the rendered card fragment without full page refresh.
  - If title is empty or whitespace-only, submission is blocked or returns an inline validation error.
  - Column counter increments immediately.

### US-3: Drag and Drop Reordering (Within and Across Columns)
* **As a** user,
* **I want to** drag a card within its column or drop it into a different column,
* **So that** I can adjust task priorities and change task status.
* **Acceptance Criteria:**
  - Dragging is powered by SortableJS on cards.
  - Dropping triggers Sortable's `onEnd` callback, dispatching an HTMX `PATCH /cards/{id}/move` request with `target_column_id`, `prev_card_id`, and `next_card_id`.
  - Backend updates the card's column and computes the new `rank`.
  - Counter pills for origin and destination columns update automatically.

### US-4: Edit Card Details
* **As a** user,
* **I want to** click a card to open a modal dialog and edit its title, description, and label color,
* **So that** I can keep task details up to date.
* **Acceptance Criteria:**
  - Clicking a card triggers `hx-get="/cards/{id}/edit"` swapped into `#modal-container`.
  - Saving submits `hx-put="/cards/{id}"`, updating the card and swapping the updated card HTML in-place.
  - Pressing `Esc` or clicking the backdrop closes the modal.

### US-5: Delete a Card
* **As a** user,
* **I want to** delete a card with confirmation,
* **So that** I can prune unwanted tasks.
* **Acceptance Criteria:**
  - Card or edit modal provides a `Delete` button with browser confirmation.
  - Submitting `hx-delete="/cards/{id}"` removes the card from the DOM and decrements the column counter.

---

## 5. API & Hypermedia Contract

FastAPI delivers server-rendered Jinja2 HTML fragments when called by HTMX, or JSON responses for headless testing.

| Endpoint | Method | Input / Payload | Returns | Description |
| --- | --- | --- | --- | --- |
| `/` | `GET` | None | Full HTML Page (`index.html`) | Renders board layout and seeded cards |
| `/cards/new` | `GET` | `col_id` (query) | HTML Fragment (`card_form.html`) | Inline form for card creation |
| `/cards` | `POST` | Form: `title`, `column_id`, `description?` | HTML Fragment (`card.html`) | Creates card, updates counter via `HX-Trigger` |
| `/cards/{id}` | `GET` | None | HTML Fragment (`card_detail.html`) | Returns card detail modal |
| `/cards/{id}/edit` | `GET` | None | HTML Fragment (`modal_edit.html`) | Returns modal form for editing card |
| `/cards/{id}` | `PUT` | Form: `title`, `description`, `color` | HTML Fragment (`card.html`) | Updates card fields, swaps card outerHTML |
| `/cards/{id}` | `DELETE` | None | `200 OK` (Empty string) | Deletes record, triggers counter recalculation |
| `/cards/{id}/move` | `PATCH` | Form: `target_column_id`, `prev_card_id?`, `next_card_id?` | `204 No Content` | Calculates new float rank and updates column |

---

## 6. Frontend Component & Template Breakdown

```
app/templates/
├── base.html              # HTML shell: Tailwind CDN, HTMX 2.x, SortableJS, modal container
├── index.html             # Main view rendering top bar, board grid, and column partials
└── components/
    ├── column.html        # Column container, header with badge, drop zone, add trigger
    ├── card.html          # Card element with drag handle, labels, and HTMX triggers
    ├── card_form.html     # Inline form snippet for adding a new card
    └── modal_edit.html    # Modal dialog for editing title, description, and color
```

---

## 7. Phased Implementation Roadmap

### Phase 1: Frontend with In-Memory Dummy Backend & Testing
* **Goal:** A complete, interactive Kanban web app running entirely on FastAPI + Jinja2 + in-memory state.
* **Storage:** Python `InMemoryBoardRepository` seeded with sample columns and cards.
* **Features:** Full 4-column layout, SortableJS drag & drop, inline card creation, modal editing, card deletion, and counter updates.
* **Verification:** Pytest test suite (`uv run pytest`) testing all endpoints and HTML fragments against the in-memory repository.

### Phase 2: Persistent Backend Integration (SQLite + SQLModel) & Testing
* **Goal:** Replace in-memory dummy repository with SQLite persistence while keeping all frontend interactions intact.
* **Storage:** `SQLiteBoardRepository` using SQLModel / SQLAlchemy with automatic table creation and default seeding.
* **Features:** Real DB transactions, database-backed float ranking logic, rebalancing trigger when precision limits are reached, foreign key cascade deletions.
* **Verification:** Unit tests for float ranking math and full integration tests for SQLite persistence across application restarts.

### Phase 3: Local Deployment via Docker Compose
* **Goal:** Reproducible, single-command local deployment with persistent data.
* **Setup:**
  * Multi-stage `Dockerfile` using `uv` for minimal image size and fast build.
  * `docker-compose.yml` mounting a local directory/volume for `kanban.db`.
  * `Makefile` or shell scripts with `dev`, `test`, and `run` commands.
* **Verification:** Container healthcheck passes and data persists across `docker compose down` and `docker compose up`.

---

## 8. Success Criteria & Verification

1. **Deterministic Tooling:** All dependencies installed via `uv add` and executed with `uv run`.
2. **Zero Node Build:** Application runs cleanly in browser without `package.json`, Node, or npm.
3. **Hypermedia Architecture:** All updates driven by HTMX partial swaps and SortableJS events.
4. **Data Integrity:** In Phase 2 & 3, restarting the service/container preserves all card positions and column assignments.
5. **Quality Gates:** 100% test pass rate on `uv run pytest` across both Phase 1 and Phase 2 test suites.