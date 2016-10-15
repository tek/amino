import abc
from typing import TypeVar, Generic, Callable
import operator

from lenses import lens, Lens

from amino.tc.base import TypeClass
from amino.tc.functor import Functor
from amino.func import curried
from amino.maybe import Maybe, Empty, Just
from amino.boolean import Boolean
from amino import _

F = TypeVar('F')
G = TypeVar('G')
A = TypeVar('A')
B = TypeVar('B')
Z = TypeVar('Z')


class Foldable(Generic[F], TypeClass):
    # FIXME lens functions return index lenses, which is not a property of
    # Foldable

    @abc.abstractmethod
    def with_index(self, fa: F) -> F:
        ...

    @abc.abstractmethod
    def filter(self, fa: F, f: Callable[[A], bool]) -> F:
        ...

    def filter_not(self, fa: F, f: Callable[[A], bool]) -> F:
        pred = lambda a: not f(a)
        return self.filter(fa, pred)

    def filter_type(self, fa: F, tpe: type) -> F:
        pred = lambda a: isinstance(a, tpe)
        return self.filter(fa, pred)

    @abc.abstractmethod
    def find(self, fa: F, f: Callable[[A], bool]) -> Maybe[A]:
        ...

    @abc.abstractmethod
    @curried
    def fold_left(self, fa: F, z: Z, f: Callable[[Z, A], Z]) -> Z:
        ...

    def fold_map(self, fa: F, z: B, f: Callable[[A], B],
                 g: Callable[[Z, B], Z]=operator.add) -> Z:
        ''' map `f` over the traversable, then fold over the result
        using the supplied initial element `z` and operation `g`,
        defaulting to addition for the latter.
        '''
        mapped = Functor[type(fa)].map(fa, f)
        return self.fold_left(mapped)(z)(g)

    @abc.abstractmethod
    def find_map(self, fa: F, f: Callable[[A], Maybe[B]]) -> Maybe[B]:
        ...

    def find_type(self, fa: F, tpe: type):
        pred = lambda a: isinstance(a, tpe)
        return self.find(fa, pred)

    @abc.abstractmethod
    def index_where(self, fa: F, f: Callable[[A], bool]) -> Maybe[int]:
        ...

    def index_of(self, fa: F, a: A) -> Maybe[int]:
        return self.index_where(fa, _ == a)

    def exists(self, fa: F, f: Callable[[A], bool]) -> Boolean:
        return Boolean(self.find(fa, f).is_just)

    def contains(self, fa, v):
        return self.exists(fa, _ == v)

    def lens(self, fa: F, f: Callable[[A], bool]) -> Maybe[Lens]:
        return self.index_where(fa, f) / (lambda i: lens()[i])

    def find_lens(self, fa: F, f: Callable[[A], Maybe[Lens]]) -> Maybe[Lens]:
        check = lambda a: f(a[1]) / (lambda b: (a[0], b))
        index = lambda i, l: lens()[i].add_lens(l)
        wi = self.with_index(fa)
        return self.find_map(wi, check).map2(index)

    def find_lens_pred(self, fa: F, f: Callable[[A], bool]) -> Maybe[Lens]:
        g = lambda a: Boolean(f(a)).maybe(lens())
        return self.find_lens(fa, g)

    def _min_max(self, fa: F, f: Callable[[A], int],
                 pred: Callable[[A, A], A]) -> Maybe[A]:
        def folder(z, a):
            return (
                z.map(lambda b: b if pred(f(b), f(a)) else a)
                .or_else(Just(a))
            )
        return self.fold_left(fa, Empty())(folder)

    def max_by(self, fa: F, f: Callable[[A], int]) -> Maybe[A]:
        return self._min_max(fa, f, operator.gt)

    def min_by(self, fa: F, f: Callable[[A], int]) -> Maybe[A]:
        return self._min_max(fa, f, operator.lt)

__all__ = ('Foldable',)
