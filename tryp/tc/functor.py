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

__all__ = ('Functor')
