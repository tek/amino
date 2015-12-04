from typing import TypeVar, Dict, Generic, Tuple

from toolz import dicttoolz  # type: ignore

from tryp.maybe import may

A = TypeVar('A')
B = TypeVar('B')


class Map(Dict[A, B], Generic[A, B]):  # type: ignore

    @may
    def get(self, key):
        return Dict.get(self, key)

    def __add__(self, item: Tuple[A, B]):
        return Map(dicttoolz.assoc(self, *item))

    def __pow__(self, other: 'Map[A, B]'):
        return Map(dicttoolz.merge(self, other))

__all__ = ['Map']
