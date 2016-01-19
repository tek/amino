import abc
from typing import TypeVar, Generic, Callable

from tryp.typeclass import TypeClass

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class FlatMap(Generic[F], TypeClass):

    @abc.abstractmethod
    def flat_map(self, fa: F, f: Callable[[A], F]) -> F:
        ...

__all__ = ('FlatMap')
