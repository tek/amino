from typing import Any

from amino.options import development
from amino.util.mod import unsafe_import_name

_ = None
__ = None
L = None


def set(mod: str) -> None:
    def name(name: str) -> Any:
        return unsafe_import_name(mod, name)
    global _, __, L, MethodRef
    _ = name('_')
    __ = name('__')
    L = name('L')


def set_debug() -> None:
    set('amino.anon.debug')


def set_prod() -> None:
    set('amino.anon.prod')

if development:
    set_debug()
else:
    set_prod()

__all__ = ('set_debug', 'set_prod', '_', '__', 'MethodRef', 'L')
