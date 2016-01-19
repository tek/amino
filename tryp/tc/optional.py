import abc
from typing import TypeVar, Generic, Callable, Union

from tryp.tc.base import TypeClass
import tryp.maybe

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Optional(Generic[F], TypeClass):

    @abc.abstractmethod
    def to_maybe(self, fa: F) -> 'tryp.maybe.Maybe[B]':
        ...

    def get_or_else(self, fa: F, a: Union[A, Callable[[], A]]):
        return self.to_maybe(fa).get_or_else(a)

    __or__ = get_or_else

__all__ = ('Optional')
