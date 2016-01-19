import abc
from typing import TypeVar, Generic

from tryp.tc.apply import Apply

F = TypeVar('F')
A = TypeVar('A')


class Applicative(Generic[F], Apply):

    @abc.abstractmethod
    def pure(self, a: A) -> F:
        ...

__all__ = ('Applicative')
