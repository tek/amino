from typing import Tuple, TypeVar

from amino import curried, Maybe, Just, Nothing

A = TypeVar('A')


@curried
def lift_tuple(index: int, data: Tuple[A, ...]) -> Maybe[A]:
    return Just(data[index]) if len(data) > index else Nothing

__all__ = ('lift_tuple',)
