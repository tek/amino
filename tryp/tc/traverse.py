import abc
from typing import TypeVar, Generic, Callable

from tryp.tc.base import TypeClass  # type: ignore

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Traverse(Generic[F], TypeClass):

    @abc.abstractmethod
    def with_index(self, fa: F) -> F:
        ...

    @abc.abstractmethod
    def filter(self, fa: F, f: Callable[[A], bool]):
        ...

    def filter_not(self, fa: F, f: Callable[[A], bool]):
        return self.filter(fa, lambda a: not f(a))

__all__ = ('Traverse',)
