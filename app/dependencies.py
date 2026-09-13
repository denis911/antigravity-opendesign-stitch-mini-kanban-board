import os
from app.repositories.base import BoardRepository
from app.repositories.memory import InMemoryBoardRepository
from app.repositories.sqlite import SQLiteBoardRepository
from app.db.session import init_db

_in_memory_repo: InMemoryBoardRepository | None = None
_sqlite_repo: SQLiteBoardRepository | None = None


def get_repository() -> BoardRepository:
    """
    Dependency provider for BoardRepository.
    Defaults to SQLiteBoardRepository, falling back to InMemoryBoardRepository if REPO_TYPE=memory.
    """
    global _in_memory_repo, _sqlite_repo
    repo_type = os.getenv("REPO_TYPE", "sqlite").lower()

    if repo_type == "memory":
        if _in_memory_repo is None:
            _in_memory_repo = InMemoryBoardRepository()
        return _in_memory_repo

    if _sqlite_repo is None:
        init_db()
        _sqlite_repo = SQLiteBoardRepository()
    return _sqlite_repo
