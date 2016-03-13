import abc
from typing import TypeVar, Generic, Callable, Union

from tryp.tc.base import TypeClass
from tryp import maybe  # NOQA

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Optional(Generic[F], TypeClass):

    @abc.abstractmethod
    def to_maybe(self, fa: F) -> 'maybe.Maybe[B]':
        ...

    def get_or_else(self, fa: F, a: Union[A, Callable[[], A]]):
        return self.to_maybe(fa).get_or_else(a)

    @abc.abstractmethod
    def to_either(self, fb: F, left: A) -> 'Either[A, B]':  # type: ignore
        ...

    __or__ = get_or_else

    def contains(self, fa: F, item):
        return self.to_maybe(fa).contains(item)

__all__ = ('Optional',)
