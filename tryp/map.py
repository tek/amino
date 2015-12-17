from typing import TypeVar, Dict, Generic, Tuple, Callable

from toolz import dicttoolz  # type: ignore
from fn import _  # type: ignore

from tek.tools import find  # type: ignore

from tryp.maybe import may, Maybe
from tryp.list import List

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
D = TypeVar('D')


class Map(Dict[A, B], Generic[A, B]):  # type: ignore

    @staticmethod
    def wrap(d: Dict[A, B]) -> 'Map[A, B]':
        return Map(d)

    @may
    def get(self, key):
        return Dict.get(self, key)

    def __add__(self, item: Tuple[A, B]):
        return Map(dicttoolz.assoc(self, *item))

    def __pow__(self, other: 'Map[A, B]'):
        return Map(dicttoolz.merge(self, other))

    def find(self, f: Callable[[B], bool]) -> Maybe[Tuple[A, B]]:
        return Maybe(find(lambda a: f(self[a]), self.keys_view))\
            .map(lambda k: (k, self[k]))

    def find_key(self, f: Callable[[A], bool]) -> Maybe[Tuple[A, B]]:
        return Maybe(find(f, self.keys_view))\
            .map(lambda k: (k, self[k]))

    def valfilter(self, f: Callable[[B], bool]) -> 'Map[A, B]':
        return Map(dicttoolz.valfilter(f, self))

    def keyfilter(self, f: Callable[[A], bool]) -> 'Map[A, B]':
        return Map(dicttoolz.keyfilter(f, self))

    def filter(self, f: Callable[[Tuple[A, B]], bool]) -> 'Map[A, B]':
        return Map(dicttoolz.itemfilter(f, self))

    def valmap(self, f: Callable[[B], C]) -> 'Map[A, C]':
        return Map(dicttoolz.valmap(f, dict(self)))

    def keymap(self, f: Callable[[A], C]) -> 'Map[C, B]':
        return Map(dicttoolz.keymap(f, dict(self)))

    def map(self, f: Callable[[Tuple[A, B]], Tuple[C, D]]) -> 'Map[C, D]':
        return Map(dicttoolz.itemmap(f, self))

    def flat_map(
            self,
            f: Callable[[A, B], Maybe[Tuple[C, D]]]
    ) -> 'Map[C, D]':
        filtered = List.wrap([f(a, b) for a, b in self.items()])\
            .flatten
        return Map(filtered)

    @property
    def toList(self):
        return List.wrap(self.items())

    @property
    def head(self):
        return self.toList.head

    @property
    def keys_view(self):
        return Dict.keys(self)

    @property
    def values_view(self):
        return Dict.values(self)

    @property
    def keys(self):
        return List(*Dict.keys(self))

    @property
    def values(self):
        return List(*Dict.values(self))

    @property
    def is_empty(self):
        return self.keys.is_empty

    def at(self, *keys):
        return self.keyfilter(lambda a: a in keys)

__all__ = ['Map']
