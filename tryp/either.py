from typing import TypeVar, Generic, Callable, Union  # type: ignore

from tryp import Empty, Just, Map
from tryp.tc.base import Implicits, tc_prop
from tryp.tc.base import ImplicitInstances
from tryp.lazy import lazy
from tryp.tc.optional import Optional
from tryp.tc.monad import Monad

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class EitherInstances(ImplicitInstances):

    @lazy
    def _instances(self):
        return Map({Monad: EitherMonad(), Optional: EitherOptional()})


class Either(Generic[A, B], Implicits, implicits=True):

    def __init__(self, value: Union[A, B]):
        self.value = value

    @property
    def is_right(self):
        return isinstance(self, Right)

    @property
    def is_left(self):
        return isinstance(self, Left)

    def leffect(self, f):
        if self.is_left:
            f(self.value)
        return self


class Right(Either):
    pass


class Left(Either):
    pass


class EitherMonad(Monad):

    def pure(self, a: A):
        return Right(a)

    def flat_map(self, fa: Either[A, B], f: Callable[[B], Either[A, C]]
                 ) -> Either[A, C]:
        return f(fa.value) if isinstance(fa, Right) else fa


class EitherOptional(Optional):

    @tc_prop
    def to_maybe(self, fa: Either):
        return Just(fa.value) if fa.is_right else Empty()

__all__ = ['Either', 'Left', 'Right']
