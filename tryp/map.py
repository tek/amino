from typing import TypeVar, Dict, Generic, Tuple, Callable

from toolz import dicttoolz  # type: ignore

from tryp.maybe import may, Maybe, Just  # type: ignore
from tryp.list import List  # type: ignore
from tryp.boolean import Boolean  # type: ignore

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

    def get_all(self, *keys):
        def append(zm, k):
            return zm.flat_map(
                lambda z: self.get(k).map(lambda a: z + List(a))
            )
        return List(*keys).fold_left(Just(List()))(append)

    def get_or_else(self, key, default: Callable[[], C]):
        return self.get(key).get_or_else(default)

    def set_if_missing(self, key: A, default: Callable[[], B]):
        if key in self:
            return self
        else:
            return self + (key, default())

    def __str__(self):
        return str(dict(self))

    def __add__(self, item: Tuple[A, B]):
        return Map(dicttoolz.assoc(self, *item))

    def __pow__(self, other: 'Map[A, B]'):
        return Map(dicttoolz.merge(self, other))

    def __sub__(self, key: A):
        return Map(dicttoolz.dissoc(self, key))

    def find(self, f: Callable[[B], bool]) -> Maybe[Tuple[A, B]]:
        return self.to_list.find(lambda item: f(item[1]))

    def find_key(self, f: Callable[[A], bool]) -> Maybe[Tuple[A, B]]:
        return self.to_list.find(lambda item: f(item[0]))

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
    def to_list(self):
        return List.wrap(self.items())

    @property
    def head(self):
        return self.to_list.head

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

    def has_key(self, name):
        return Boolean(name in self)

__all__ = ['Map']
