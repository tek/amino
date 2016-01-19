import abc
from typing import TypeVar

from tryp.tc.functor import Functor

F = TypeVar('F')
A = TypeVar('A')


class Apply(Functor):

    @abc.abstractmethod
    def ap(self, fa: F, f: F) -> F:
        ''' f should be an F[Callable[[A], B]]
        '''
        ...

__all__ = ('Apply')
