from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="FastKanban",
    description="Zen Minimalist Kanban board built with FastAPI, HTMX, and Tailwind CSS",
    version="0.1.0",
)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/api/columns")
async def api_columns():
    from app.dependencies import get_repository
    repo = get_repository()
    return repo.list_columns()
