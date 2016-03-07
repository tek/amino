from typing import TypeVar, Callable

from tryp.tc.flat_map import FlatMap
from tryp.tc.applicative import Applicative

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Monad(FlatMap, Applicative):

    def map(self, fa: F, f: Callable[[A], B]) -> F:  # type: ignore
        return self.flat_map(fa, lambda a: self.pure(f(a)))

__all__ = ('Monad',)
