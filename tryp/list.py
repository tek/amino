import itertools
import typing
from typing import TypeVar, Callable, Generic, Iterable

from fn import _  # type: ignore

from tek.tools import find  # type: ignore

from tryp.maybe import Maybe

A = TypeVar('A', covariant=True)
B = TypeVar('B')


def flatten(l: Iterable[Iterable[A]]) -> Iterable[A]:
    return list(itertools.chain.from_iterable(l))  # type: ignore


class List(typing.List[A], Generic[A]):

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

    def flat_map(self, f: Callable[[A], 'Iterable[B]']) -> 'List[B]':
        return List.wrap(flatten(map(f, self)))

    @property
    def flatten(self):
        return self.flat_map(lambda a: a)

    def foreach(self, f: Callable[[A], B]) -> None:
        for el in self:
            f(el)

    def find(self, f: Callable[[A], bool]):
        return Maybe(find(f, self))

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

__all__ = ['List']
