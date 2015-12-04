import itertools
import typing
from typing import TypeVar, Callable, Generic, Iterable

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
        return Maybe.from_call(self.__getitem__, index)

    def map(self, f: Callable[[A], B]) -> 'List[B]':
        return List.wrap(list(map(f, self)))

    def flatMap(self, f: Callable[[A], 'Iterable[B]']) -> 'List[B]':
        return List.wrap(flatten(map(f, self)))

    def find(self, f: Callable[[A], bool]):
        return Maybe(find(f, self))

__all__ = ['List']
