import abc
from typing import TypeVar, Generic

from tryp.tc.functor import Functor

F = TypeVar('F')
A = TypeVar('A')


class Apply(Generic[F], Functor):

    @abc.abstractmethod
    def ap(self, fa: F, f: F) -> F:
        ''' f should be an F[Callable[[A], B]]
        '''
        ...

__all__ = ('Apply')
