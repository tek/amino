from typing import TypeVar, Callable

from tryp.tc.flat_map import FlatMap
from tryp.tc.applicative import Applicative
from tryp.tc.base import tc_prop
from tryp import List

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Monad(FlatMap, Applicative):

    def map(self, fa: F, f: Callable[[A], B]) -> F:  # type: ignore
        return self.flat_map(fa, lambda a: self.pure(f(a)))

    def eff(self, fa: F, tpe: type):
        from tryp.eff import Eff
        return Eff(fa)

    def effs(self, fa: F, depth: int, *types):
        from tryp.eff import Eff
        return Eff(fa, List.wrap(types), depth=depth)

__all__ = ('Monad',)
