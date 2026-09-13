from fastapi import FastAPI, Request, Depends
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


@app.get("/api/columns")
async def api_columns(repo: BoardRepository = Depends(get_repository)):
    return repo.list_columns()
