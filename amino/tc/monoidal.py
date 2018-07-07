import abc
from typing import TypeVar, Generic

from amino.tc.base import TypeClass

F = TypeVar('F')


class Monoidal(TypeClass):

    @abc.abstractmethod
    def product(self, fa: F, fb: F) -> F:
        ...

__all__ = ('Monoidal',)
