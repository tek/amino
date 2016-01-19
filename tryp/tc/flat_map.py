import abc
from typing import TypeVar, Generic, Callable

from tryp.tc.apply import Apply

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class FlatMap(Generic[F], Apply):

    def ap(self, fa: F, ff: F):
        return self.flat_map(ff, lambda f: self.map(fa, f))

    @abc.abstractmethod
    def flat_map(self, fa: F, f: Callable[[A], F]) -> F:
        ...

    def __floordiv__(self, fa, f):
        return self.flat_map(fa, f)

__all__ = ('FlatMap')
