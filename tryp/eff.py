from typing import Callable

from tryp.anon import __


class Eff:

    def __init__(self, value, depth: int=1) -> None:
        self.value = value
        self.depth = depth

    def _map(self, f: Callable):
        from tryp.list import List
        g = List.wrap(range(self.depth)).fold_left(f)(lambda z, i: __.map(z))
        return g(self.value)

    def map(self, f: Callable) -> 'Eff':
        return Eff(self._map(__.map(f)))

    __truediv__ = map

    def flat_map(self, f: Callable):
        return Eff(self.value.map(__.flat_map(f)))

    __floordiv__ = flat_map

__all__ = ('Eff',)
