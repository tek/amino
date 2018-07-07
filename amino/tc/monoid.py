import abc
from typing import TypeVar

from amino.tc.base import TypeClass

A = TypeVar('A')


class Monoid(TypeClass):

    @abc.abstractproperty
    def empty(self) -> A:
        ...

    @abc.abstractmethod
    def combine(self, a: A, b: A) -> A:
        ...

__all__ = ('Monoid',)
