import abc
from typing import TypeVar, Generic, Callable

from tryp.typeclass import TypeClass

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Functor(Generic[F], TypeClass):

    @abc.abstractmethod
    def map(self, fa: F, f: Callable[[A], B]) -> B:
        ...

__all__ = ('Functor')
