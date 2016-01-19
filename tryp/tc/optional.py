import abc
from typing import TypeVar, Generic, Callable

from tryp.tc.base import TypeClass, tc_prop
import tryp.maybe

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Optional(Generic[F], TypeClass):

    @abc.abstractmethod
    def to_maybe(self, fa: F) -> 'tryp.maybe.Maybe[B]':
        ...

__all__ = ('Optional')
