import abc
from typing import TypeVar, Generic, Callable

from tryp.tc.base import TypeClass  # type: ignore

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Functor(Generic[F], TypeClass):

    @abc.abstractmethod
    def map(self, fa: F, f: Callable[[A], B]) -> F:
        ...

    def __truediv__(self, fa, f):
        return self.map(fa, f)

    def smap(self, fa: F, f: Callable[..., B]) -> F:
        return self.map(fa, lambda v: f(*v))

    def ssmap(self, fa: F, f: Callable[..., B]) -> F:
        return self.map(fa, lambda v: f(**v))

__all__ = ('Functor',)
