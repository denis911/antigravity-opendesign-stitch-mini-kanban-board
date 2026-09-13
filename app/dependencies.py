from functools import lru_cache
from app.repositories.base import BoardRepository
from app.repositories.memory import InMemoryBoardRepository


# Singleton instance for dummy in-memory backend
_in_memory_repo = InMemoryBoardRepository()


def get_repository() -> BoardRepository:
    return _in_memory_repo
