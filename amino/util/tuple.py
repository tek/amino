from typing import Tuple, TypeVar, Callable

from amino import Maybe, Just, Nothing

A = TypeVar('A')


def lift_tuple(index: int) -> Callable[[Tuple[A, ...]], Maybe[A]]:
    def lift_tuple(data: Tuple[A, ...]) -> Maybe[A]:
        return Just(data[index]) if len(data) > index else Nothing
    return lift_tuple

__all__ = ('lift_tuple',)
