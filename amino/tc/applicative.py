import abc
from typing import TypeVar

from amino.tc.apply import Apply

F = TypeVar('F')
A = TypeVar('A')


class Applicative(Apply):

    @abc.abstractmethod
    def pure(self, a: A) -> F:
        ...

__all__ = ('Applicative',)
