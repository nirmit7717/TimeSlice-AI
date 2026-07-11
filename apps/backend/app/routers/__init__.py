from .processes import router as processes_router
from .slices import router as slices_router
from .scheduler import router as scheduler_router
from .vault import router as vault_router
from .chat import router as chat_router
from .sync import router as sync_router

__all__ = [
    "processes_router",
    "slices_router",
    "scheduler_router",
    "vault_router",
    "chat_router",
    "sync_router"
]
