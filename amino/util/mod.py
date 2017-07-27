import importlib
from typing import Optional, Any


def unsafe_import_name(modname: str, name: str) -> Optional[Any]:
    mod = importlib.import_module(modname)
    return getattr(mod, name) if hasattr(mod, name) else None

__all__ = ('unsafe_import_name',)
