import abc
from typing import TypeVar

from tryp.tc.apply import Apply

F = TypeVar('F')
A = TypeVar('A')


class Applicative(Apply):

    @abc.abstractmethod
    def pure(self, a: A) -> F:
        ...

__all__ = ('Applicative',)
