import abc
from typing import TypeVar, Generic, Callable

from amino.tc.base import TypeClass
from amino.func import I

F = TypeVar('F')
G = TypeVar('G')
A = TypeVar('A')
B = TypeVar('B')
Z = TypeVar('Z')


class Traverse(Generic[F], TypeClass):
    # FIXME lens functions return index lenses, which is not a property of
    # Traverse

    @abc.abstractmethod
    def traverse(self, fa: F, f: Callable, tpe: type):
        ...

    def sequence(self, fa: F, tpe: type):
        return self.traverse(fa, I, tpe)

__all__ = ('Traverse',)
