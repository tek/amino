import abc
from typing import TypeVar, Generic, Callable

from amino.tc.base import TypeClass

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Zip(Generic[F], TypeClass):

    @abc.abstractmethod
    def zip(self, fa: F, fb: F, *fs) -> F:
        ...

    def __and__(self, fa: F, fb: F):
        return self.zip(fa, fb)

    def apzip(self, fa: F, f: Callable[[A], B]) -> F:
        return self.zip(fa, fa.map(f))  # type: ignore

__all__ = ('Zip',)
