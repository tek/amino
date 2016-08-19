from typing import TypeVar, Generic, Callable

from amino.tc.base import TypeClass
from amino.tc.monad import Monad

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Tap(Generic[F], TypeClass):

    def tap(self, fa: F, f: Callable[[A], B]) -> F:
        def effect(a):
            f(a)
            return fa
        return Monad[type(fa)].flat_map(fa, effect)  # type: ignore

    def __mod__(self, fa, f):
        return self.tap(fa, f)

__all__ = ('Tap',)
