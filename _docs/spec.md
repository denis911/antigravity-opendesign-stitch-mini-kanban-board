# Project Specification: FastKanban (HTMX + FastAPI)

## 1. Overview & Problem Statement

Modern Kanban applications frequently suffer from excessive client-side bloat, vendor lock-in, and fragile build chains.

**FastKanban** is a lightweight, full-stack, local-first Kanban board built on the principle of hypermedia-driven architecture. It provides an intuitive, friction-free task management experience using server-rendered HTML fragments and declarative UI interactions, eliminating client-side state managers and Node-based compilation pipelines.

### 1.1 Goals

* Zero-build frontend: Runs directly in modern browsers using plain HTML5, HTMX, Tailwind CSS (via CDN or standalone CLI), and SortableJS.
* Deterministic, predictable backend: FastAPI service utilizing SQLite with clean schema definitions.
* Offline & self-contained: Fully runnable via Docker Compose on a single machine or deployable to a free-tier single-container host (Render, Fly.io, or GCP Cloud Run).
* Spec-driven development: Clear contracts between the hypermedia UI layer and HTTP endpoints.

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
  └─ Tailwind CSS (Styling via utility classes)
        │
        ▼ HTTP (HTML Fragments & JSON)
[ FastAPI Backend ]
  │
  ├─ Jinja2Templates (Server-rendered components/fragments)
  ├─ Pydantic v2 (Input validation & schemas)
  └─ SQLModel / SQLAlchemy (ORM Layer)
        │
        ▼
[ SQLite Engine ] (Mounted file: `kanban.db`)

```

### 2.1 Technology Choices

* **Frontend:** HTMX (`v2.0.x`), Tailwind CSS (`v3.x` CDN or pre-compiled standalone), SortableJS (`v1.15.x`).
* **Backend:** Python 3.11+, FastAPI (`>=0.110`), Uvicorn, Jinja2.
* **Database & Persistence:** SQLite with Write-Ahead Logging (WAL) enabled; SQLModel/SQLAlchemy for typed models and migrations.
* **Containerization:** Multi-stage `Dockerfile` with volume-backed persistence for SQLite.

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

* `id`: `TEXT` (Primary Key, e.g., `col-todo`, `col-in-progress`, `col-done`, or UUIDv4).
* `title`: `VARCHAR(100)`, Not Null.
* `position`: `INTEGER`, Not Null (0-indexed sequence of columns across the board).
* `created_at`: `DATETIME`, Default UTC current timestamp.

#### Cards (`cards`)

* `id`: `TEXT` (Primary Key, UUIDv4 prefix: `card_xxxx`).
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


* Moving to the top of a column: $\text{New Rank} = \frac{R_{\text{first}}}{2}$
* Moving to the bottom of a column: $\text{New Rank} = R_{\text{last}} + 1000.0$
* Rebalance trigger: If $\vert{}R_A - R_B\vert{} < 1e-6$, a background task re-spaces column ranks to $[1000, 2000, 3000...]$.

---

## 4. User Stories & Acceptance Criteria

### US-1: View Board and Columns

* **As a** user,
* **I want to** load the main page and view all default columns (*Backlog*, *In Progress*, *Review*, *Done*) with their cards,
* **So that** I have immediate visibility over active work.
* **Acceptance Criteria:**
* Page loads with a standard 4-column responsive grid layout.
* Each column displays its title, dynamic card counter pill, and a card list container.
* Empty columns render a subtle placeholder drop zone.



### US-2: Create a New Card

* **As a** user,
* **I want to** add a new card to any column using an inline form or button,
* **So that** I can capture tasks quickly.
* **Acceptance Criteria:**
* Each column footer has an `+ Add Card` button.
* Clicking displays a lightweight inline form (Title input, Add and Cancel buttons).
* Submitting via `Enter` or `Add` sends an HTMX request that prepends or appends the rendered card fragment without refreshing the page.
* If title is empty, form returns a visual validation error.



### US-3: Drag and Drop Reordering (Within and Across Columns)

* **As a** user,
* **I want to** drag a card within its column or drop it into a different column,
* **So that** I can adjust task priorities and change task status.
* **Acceptance Criteria:**
* Dragging is initiated via SortableJS on `.kanban-card` elements.
* Dropping triggers Sortable's `onEnd` callback, dispatching an HTMX `PATCH` request with `card_id`, `target_column_id`, and adjacent sibling card IDs.
* Server computes the updated `rank` and `column_id`, updates SQLite, and returns `204 No Content` or the updated card fragment.
* Counter pills for origin and destination columns update automatically.



### US-4: Edit Card Details

* **As a** user,
* **I want to** click a card to open a modal dialog and edit its title, description, and label color,
* **So that** I can keep task details up to date.
* **Acceptance Criteria:**
* Clicking a card requests the edit modal fragment via `hx-get="/cards/{id}/edit"` swapped into `#modal-container`.
* Saving submits `hx-put="/cards/{id}"`, updating the record and swapping the refreshed card in-place using `hx-swap="outerHTML"`.
* Pressing `Esc` or clicking the backdrop closes the modal.



### US-5: Delete a Card

* **As a** user,
* **I want to** delete a card with confirmation,
* **So that** I can prune unwanted tasks.
* **Acceptance Criteria:**
* Card or edit modal provides a `Delete` button with `hx-confirm="Are you sure?"`.
* Submitting `hx-delete="/cards/{id}"` returns a `200 OK` with an empty string, removing the element from the DOM and updating the column counter.



---

## 5. API & Hypermedia Contract

FastAPI delivers server-rendered Jinja2 HTML fragments when called by HTMX (detected by the presence of the `HX-Request: true` header), or JSON responses for headless interaction.

| Endpoint | Method | Input / Payload | Returns | Description |
| --- | --- | --- | --- | --- |
| `/` | `GET` | None | Full HTML Page | Renders primary layout and initial state |
| `/cards/new` | `GET` | `col_id` (query) | HTML Fragment | Inline form for card creation |
| `/cards` | `POST` | Form: `title`, `column_id`, `description?` | HTML Fragment (`card.html`) | Creates card, updates counter via `HX-Trigger` |
| `/cards/{id}` | `GET` | None | HTML Fragment (`card_detail.html`) | Returns card detail modal |
| `/cards/{id}/edit` | `GET` | None | HTML Fragment (`card_edit.html`) | Returns modal form for editing card |
| `/cards/{id}` | `PUT` | Form: `title`, `description`, `color` | HTML Fragment (`card.html`) | Updates card fields, swaps card outerHTML |
| `/cards/{id}` | `DELETE` | None | Empty response / 200 | Deletes record, triggers counter recalculation |
| `/cards/{id}/move` | `PATCH` | Form/JSON: `target_col_id`, `prev_card_id?`, `next_card_id?` | `204 No Content` or `card.html` | Calculates new float rank and updates column |

---

## 6. Frontend Component & Template Breakdown

```
app/templates/
├── base.html              # HTML shell: Tailwind CDN, HTMX script, SortableJS, meta tags
├── index.html             # Main view rendering top bar and iterating columns
├── components/
│   ├── column.html        # Column container, header with badge, drop zone, add trigger
│   ├── card.html          # Individual card element with drag handles and HTMX attributes
│   ├── card_form.html     # Inline form snippet for adding a new card
│   └── modal_edit.html    # Modal dialog for editing title, description, and color

```

### 6.1 SortableJS to HTMX Bridge Pattern

SortableJS attaches to each `.kanban-cards-container`. On drop, it triggers an HTMX AJAX call with positional coordinates:

```javascript
document.querySelectorAll('.kanban-cards-container').forEach(col => {
  new Sortable(col, {
    group: 'kanban-board',
    animation: 150,
    ghostClass: 'opacity-40',
    onEnd: function (evt) {
      const itemEl = evt.item;
      const targetColId = evt.to.dataset.columnId;
      const prevCardId = itemEl.previousElementSibling?.dataset.cardId || null;
      const nextCardId = itemEl.nextElementSibling?.dataset.cardId || null;

      htmx.ajax('PATCH', `/cards/${itemEl.dataset.cardId}/move`, {
        values: {
          target_column_id: targetColId,
          prev_card_id: prevCardId,
          next_card_id: nextCardId
        },
        swap: 'none'
      });
    }
  });
});

```

---

## 7. Implementation Plan & Issue Decomposition

To prevent model context drift during execution with agentic tools (`agy`), implementation is decomposed into six focused, isolated work units:

### Issue #1: Project Structure & Base Static Prototype

* Set up directory structure: `app/`, `app/templates/`, `app/static/`, `tests/`.
* Create standalone `index.html` referencing Tailwind CSS and mock cards.
* Validate responsive grid layout and CSS hierarchy on desktop and mobile.

### Issue #2: SortableJS Integration & Frontend Mock Interaction

* Add SortableJS CDN script to `base.html`.
* Wire drag-and-drop between columns.
* Log drop coordinates (`prev_card_id`, `next_card_id`, `target_column_id`) to the browser console.

### Issue #3: Database Models & SQLite Setup

* Define SQLModel/SQLAlchemy entities (`Column`, `Card`).
* Create database initialization routine with automatic seeding of default columns (*Backlog*, *In Progress*, *Review*, *Done*).
* Write unit tests for floating-point rank calculations.

### Issue #4: Core CRUD Endpoints & Jinja2 Hypermedia Templates

* Implement FastAPI routers for `GET /`, `POST /cards`, `PUT /cards/{id}`, and `DELETE /cards/{id}`.
* Convert static mockup components into modular Jinja2 templates (`card.html`, `column.html`, `modal_edit.html`).
* Wire HTMX triggers for modal display and inline card submission.

### Issue #5: Drag-and-Drop Movement Endpoint

* Implement `PATCH /cards/{id}/move`.
* Connect Sortable's `onEnd` event to the movement endpoint using `htmx.ajax`.
* Verify database persistence across browser reloads.

### Issue #6: Dockerization & Deployment Verification

* Author multi-stage `Dockerfile` running Uvicorn on port `8000`.
* Author `docker-compose.yml` with host volume mounting for `./data/kanban.db`.
* Add Makefile/scripts for one-command test and run: `make test`, `make dev`, `make run`.

---

## 8. Success Criteria & Verification

1. **Zero Node Build:** Application runs cleanly without `package.json`, Node, or npm.
2. **Instant Visual Feedback:** Moving cards or adding tasks reflects immediately on screen with sub-50ms local latency.
3. **Data Integrity:** Restarting the Docker container preserves all card positions, column assignments, and descriptions.
4. **Test Coverage:** All card movements and ranking boundary tests in `tests/test_api.py` pass cleanly.

---