import itertools
import typing
from typing import TypeVar, Callable, Generic, Iterable, Any
from functools import reduce  # type: ignore

from fn import _  # type: ignore

from tryp.maybe import Maybe, Just, Empty
from tryp.func import curried
from tryp.logging import log
from tryp.tc.monad import Monad
from tryp.tc.base import Implicits, ImplicitInstances
from tryp.lazy import lazy

A = TypeVar('A', covariant=True)
B = TypeVar('B')


def flatten(l: Iterable[Iterable[A]]) -> Iterable[A]:
    return list(itertools.chain.from_iterable(l))  # type: ignore


class ListInstances(ImplicitInstances):

    @lazy
    def _instances(self):
        from tryp import Map
        return Map({Monad: ListMonad()})


class List(typing.List[A], Generic[A], Implicits, implicits=True):

    def __init__(self, *elements):
        typing.List.__init__(self, elements)

    @staticmethod
    def wrap(l: Iterable[B]) -> 'List[B]':
        return List(*l)

    def lift(self, index: int) -> Maybe[A]:
        return Maybe.from_call(self.__getitem__, index, exc=IndexError)

    def map(self, f: Callable[[A], B]) -> 'List[B]':
        return List.wrap(list(map(f, self)))

    def smap(self, f: Callable[..., B]) -> 'List[B]':
        return List.wrap(list(itertools.starmap(f, self)))

    def flat_smap(self, f: Callable[..., 'Iterable[B]']) -> 'List[B]':
        return List.wrap(flatten(list(itertools.starmap(f, self))))

    @property
    def flatten(self):
        return self.flat_map(lambda a: a)

    def foreach(self, f: Callable[[A], B]) -> None:
        for el in self:
            f(el)

    def find(self, f: Callable[[A], bool]):
        return Maybe(next(filter(f, self), None))

    def filter(self, f: Callable[[A], bool]):
        return List.wrap(filter(f, self))

    def contains(self, value):
        return value in self

    @property
    def is_empty(self):
        return self.length == 0

    @property
    def length(self):
        return len(self)

    @property
    def head(self):
        return self.lift(0)

    @property
    def last(self):
        return self.lift(-1)

    @property
    def distinct(self):
        seen = set()
        return List.wrap(x for x in self if x not in seen and not seen.add(x))

    def __add__(self, other: typing.List[A]) -> 'List[A]':
        return List.wrap(typing.List.__add__(self, other))

    def without(self, el) -> 'List[A]':
        return self.filter(_ != el)

    def split(self, f: Callable[[A], bool]):
        def splitter(z, e):
            l, r = z
            return (l + (e,), r) if f(e) else (l, r + (e,))
        l, r = reduce(splitter, self, ((), (),))
        return List.wrap(l), List.wrap(r)

    def split_type(self, tpe: type):
        return self.split(lambda a: isinstance(a, tpe))

    @curried
    def fold_left(self, z: B, f: Callable[[B, A], B]) -> B:
        return reduce(f, self, z)

    def debug(self, prefix=None):
        prefix = '' if prefix is None else prefix + ' '
        log.debug(prefix + str(self))
        return self

    def index_where(self, pred: Callable[[Any], bool]):
        gen = (Just(i) for i, a in enumerate(self) if pred(a))
        return next(gen, Empty())  # type: ignore

    def index_of(self, target: Any):
        return self.index_where(_ == target)

    @property
    def reversed(self):
        return List.wrap(reversed(self))


class ListMonad(Monad):

    def pure(self, a: A):
        return List(a)

    def flat_map(self, fa: List[A], f: Callable[[A], List[B]]) -> List[B]:
        return List.wrap(flatten(map(f, fa)))

__all__ = ['List']
