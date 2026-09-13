from typing import Optional
from fastapi import FastAPI, Request, Depends, Form, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.repositories.base import BoardRepository
from app.dependencies import get_repository

app = FastAPI(
    title="FastKanban",
    description="Zen Minimalist Kanban board built with FastAPI, HTMX, and Tailwind CSS",
    version="0.1.0",
)

templates = Jinja2Templates(directory="app/templates")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def read_board(
    request: Request,
    repo: BoardRepository = Depends(get_repository)
):
    columns = repo.list_columns()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"columns": columns}
    )


@app.get("/cards/new", response_class=HTMLResponse)
async def card_new_form(
    request: Request,
    col_id: str
):
    return templates.TemplateResponse(
        request=request,
        name="components/card_form.html",
        context={"column_id": col_id}
    )


@app.get("/cards/cancel-form", response_class=HTMLResponse)
async def card_cancel_form(col_id: str):
    return f"""
    <button class="w-full py-1.5 px-2.5 rounded-lg border border-dashed border-outline-variant/50 hover:border-outline text-secondary hover:text-on-surface font-mono text-xs flex items-center justify-center gap-1.5 hover:bg-surface-container transition-all"
            hx-get="/cards/new?col_id={col_id}"
            hx-target="#add-card-container-{col_id}"
            hx-swap="innerHTML">
      <span class="material-symbols-outlined text-[15px]">add</span>
      <span>Add Card</span>
    </button>
    """


@app.post("/cards", response_class=HTMLResponse)
async def create_card(
    request: Request,
    column_id: str = Form(...),
    title: str = Form(""),
    description: Optional[str] = Form(""),
    repo: BoardRepository = Depends(get_repository)
):
    cleaned_title = title.strip()
    if not cleaned_title:
        # Return form with inline error
        response = templates.TemplateResponse(
            request=request,
            name="components/card_form.html",
            context={
                "column_id": column_id,
                "title": title,
                "error": "Title cannot be empty"
            }
        )
        response.headers["HX-Retarget"] = f"#add-card-container-{column_id}"
        response.headers["HX-Reswap"] = "innerHTML"
        return response

    card = repo.create_card(
        column_id=column_id,
        title=cleaned_title,
        description=description
    )

    col = repo.get_column(column_id)
    count = len(col.cards) if col else 0

    card_html = templates.get_template("components/card.html").render({"card": card})

    oob_counter = f'<span id="counter-{column_id}" hx-swap-oob="true" class="font-mono text-[11px] text-on-surface-variant bg-surface-container px-2 py-0.5 rounded font-medium">{count:02d}</span>'

    oob_reset_btn = f"""
    <div id="add-card-container-{column_id}" hx-swap-oob="true" class="mt-2 pt-2 border-t border-outline-variant/20">
      <button class="w-full py-1.5 px-2.5 rounded-lg border border-dashed border-outline-variant/50 hover:border-outline text-secondary hover:text-on-surface font-mono text-xs flex items-center justify-center gap-1.5 hover:bg-surface-container transition-all"
              hx-get="/cards/new?col_id={column_id}"
              hx-target="#add-card-container-{column_id}"
              hx-swap="innerHTML">
        <span class="material-symbols-outlined text-[15px]">add</span>
        <span>Add Card</span>
      </button>
    </div>
    """

    oob_remove_empty = f'<div id="empty-{column_id}" hx-swap-oob="delete"></div>'

    combined_html = f"{card_html}\n{oob_counter}\n{oob_reset_btn}\n{oob_remove_empty}"
    return HTMLResponse(content=combined_html, status_code=201)


@app.delete("/cards/{card_id}", response_class=HTMLResponse)
async def delete_card(
    card_id: str,
    repo: BoardRepository = Depends(get_repository)
):
    card = repo.get_card(card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    column_id = card.column_id
    repo.delete_card(card_id)

    col = repo.get_column(column_id)
    count = len(col.cards) if col else 0

    oob_counter = f'<span id="counter-{column_id}" hx-swap-oob="true" class="font-mono text-[11px] text-on-surface-variant bg-surface-container px-2 py-0.5 rounded font-medium">{count:02d}</span>'

    return HTMLResponse(content=oob_counter, status_code=200)


@app.get("/api/columns")
async def api_columns(repo: BoardRepository = Depends(get_repository)):
    return repo.list_columns()
