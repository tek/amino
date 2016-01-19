from typing import TypeVar, Generic, Callable

from tryp.tc.flat_map import FlatMap
from tryp.tc.applicative import Applicative

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Monad(Generic[F], FlatMap, Applicative):

    def map(self, fa: F, f: Callable[[A], B]) -> F:
        return self.flat_map(fa, lambda a: self.pure(f(a)))

__all__ = ('Monad')
