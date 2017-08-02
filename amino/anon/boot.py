from typing import Any

from amino import options
from amino.util.mod import unsafe_import_name

_ = None
__ = None
L = None


def set(mod: str) -> None:
    def name(name: str) -> Any:
        return unsafe_import_name(mod, name)
    global _, __, L
    _ = name('AttrLambdaInst')
    __ = name('MethodLambdaInst')
    L = name('ComplexLambdaInit')


def set_debug() -> None:
    set('amino.anon.debug')


def set_prod() -> None:
    set('amino.anon.prod')

if options.anon_debug:
    set_debug()
else:
    set_prod()

__all__ = ('set_debug', 'set_prod', '_', '__', 'L')
