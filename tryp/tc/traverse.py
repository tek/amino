import abc
from typing import TypeVar, Generic

from tryp.tc.base import TypeClass  # type: ignore

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Traverse(Generic[F], TypeClass):

    @abc.abstractmethod
    def with_index(self, fa: F) -> F:
        ...

__all__ = ('Traverse',)
