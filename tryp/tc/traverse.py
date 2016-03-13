import abc
from typing import TypeVar, Generic, Callable

from fn import _

from tryp.tc.base import TypeClass
from tryp.tc.functor import Functor
from tryp.func import curried

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')
Z = TypeVar('Z')


class Traverse(Generic[F], TypeClass):

    @abc.abstractmethod
    def with_index(self, fa: F) -> F:
        ...

    @abc.abstractmethod
    def filter(self, fa: F, f: Callable[[A], bool]):
        ...

    def filter_not(self, fa: F, f: Callable[[A], bool]):
        return self.filter(fa, lambda a: not f(a))

    @abc.abstractmethod
    @curried
    def fold_left(self, fa: F, z: Z, f: Callable[[Z, A], Z]) -> Z:
        ...

    def fold_map(self, fa: F, z: B, f: Callable[[A], B],
                 g: Callable[[Z, B], Z]=_ + _) -> Z:
        ''' map `f` over the traversable, then fold over the result
        using the supplied initial element `z` and operation `g`,
        defaulting to addition for the latter.
        '''
        mapped = Functor[type(fa)].map(fa, f)
        return self.fold_left(mapped)(z)(g)

__all__ = ('Traverse',)
