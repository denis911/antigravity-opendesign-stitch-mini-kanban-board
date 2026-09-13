import os
from pathlib import Path
from typing import Generator
from sqlalchemy import event, Engine
from sqlmodel import SQLModel, Session, create_engine, select
from app.db.models import Column, Card

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/kanban.db")

# Ensure directory exists for SQLite
if DATABASE_URL.startswith("sqlite:///./"):
    db_rel_path = DATABASE_URL.replace("sqlite:///./", "")
    db_dir = Path(db_rel_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable SQLite WAL mode and foreign key constraint enforcement."""
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.close()
    except Exception:
        pass


def init_db(target_engine=engine) -> None:
    """Create tables and seed default columns if empty."""
    SQLModel.metadata.create_all(target_engine)

    with Session(target_engine) as session:
        existing_cols = session.exec(select(Column)).all()
        if not existing_cols:
            default_columns = [
                Column(id="col-backlog", title="Backlog", position=0),
                Column(id="col-in-progress", title="In Progress", position=1),
                Column(id="col-review", title="Review", position=2),
                Column(id="col-done", title="Done", position=3),
            ]
            for col in default_columns:
                session.add(col)
            session.commit()

            # Seed initial sample cards from Stitch design
            initial_cards = [
                Card(
                    id="card-1",
                    column_id="col-backlog",
                    title="Decouple IndexedDB sync from rendering loop",
                    description="Optimize state management by isolating database writes from main UI thread.",
                    rank=1000.0,
                    color="default",
                    code_id="ENG-204",
                    tag="perf",
                    assignee="KN"
                ),
                Card(
                    id="card-2",
                    column_id="col-backlog",
                    title="Evaluate Brotli compression for asset distribution",
                    description="Benchmark cold-start bundle sizes against gzip.",
                    rank=2000.0,
                    color="blue",
                    code_id="ENG-209",
                    tag="infra",
                    assignee="KN"
                ),
                Card(
                    id="card-3",
                    column_id="col-in-progress",
                    title="Migrate session token rotation to WebCrypto API",
                    description="Replace legacy crypto library with browser-native WebCrypto primitives.",
                    rank=1000.0,
                    color="yellow",
                    code_id="CORE-104",
                    tag="auth",
                    assignee="TA"
                ),
                Card(
                    id="card-4",
                    column_id="col-review",
                    title="Harmonize micro-typography baselines with JetBrains Mono chips",
                    description="Align letter-spacing and vertical centering on status tokens.",
                    rank=1000.0,
                    color="green",
                    code_id="ZEN-82",
                    tag="ui",
                    assignee="SS"
                ),
                Card(
                    id="card-5",
                    column_id="col-done",
                    title="Extract organic neutral tokens for Rice Paper palette",
                    description="Configure Tailwind theme extension with Washi and Sumi ink colors.",
                    rank=1000.0,
                    color="default",
                    code_id="SYS-12",
                    tag="design",
                    assignee="YS"
                ),
            ]
            for card in initial_cards:
                session.add(card)
            session.commit()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
