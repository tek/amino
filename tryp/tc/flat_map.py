import abc
from typing import TypeVar, Callable

from tryp.tc.apply import Apply

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class FlatMap(Apply):

    def ap(self, fa: F, ff: F):
        return self.flat_map(ff, lambda f: self.map(fa, f))

    @abc.abstractmethod
    def flat_map(self, fa: F, f: Callable[[A], F]) -> F:
        ...

    def flat_smap(self, fa: F, f: Callable[..., F]) -> F:
        return self.flat_map(fa, lambda v: f(*v))

    def __floordiv__(self, fa, f):
        return self.flat_map(fa, f)

__all__ = ('FlatMap')
