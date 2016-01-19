import abc
from typing import TypeVar, Generic, Callable

from tryp.typeclass import TypeClass, tc_prop
from tryp import Maybe

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Optional(Generic[F], TypeClass):

    @abc.abstractmethod
    def to_maybe(self, fa: F) -> Maybe[B]:
        ...

__all__ = ('Optional')
