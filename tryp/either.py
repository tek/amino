from typing import TypeVar, Generic, Callable, Union, Any

from tryp import maybe
from tryp.func import I
from tryp.tc.base import Implicits, tc_prop, ImplicitInstances
from tryp.lazy import lazy
from tryp.tc.optional import Optional
from tryp.tc.monad import Monad

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class EitherInstances(ImplicitInstances):

    @lazy
    def _instances(self):
        from tryp.map import Map
        return Map({Monad: EitherMonad(), Optional: EitherOptional()})


class Either(Generic[A, B], Implicits, implicits=True):

    def __init__(self, value: Union[A, B]) -> None:
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

    def cata(self, fl: Callable[[A], Any], fr: Callable[[B], Any]):
        f = fl if self.is_left else fr
        return f(self.value)  # type: ignore

    def recover_with(self, f: Callable[[A], 'Either[A, B]']):
        return self.cata(f, Right)

    def right_or_map(self, f: Callable[[A], Any]):
        return self.cata(f, I)

    def left_or_map(self, f: Callable[[B], Any]):
        return self.cata(I, f)

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, str(self.value))

    def __repr__(self):
        return str(self)

    @property
    def to_list(self):
        return self.to_maybe.to_list

    def lmap(self, f: Callable[[A], Any]):
        return Left(f(self.value)) if self.is_left else self  # type: ignore

    def zip(self, other: 'Either[Any, C]') -> 'Either[A, Tuple[B, C]]':
        if self.is_right and other.is_right:
            return Right((self.value, other.value))
        elif self.is_left:
            return self
        else:
            return other


class Right(Either):

    def __eq__(self, other):
        return isinstance(other, Right) and self.value == other.value


class Left(Either):

    def __eq__(self, other):
        return isinstance(other, Left) and self.value == other.value


class EitherMonad(Monad):

    def pure(self, a: A):
        return Right(a)

    def flat_map(self, fa: Either[A, B], f: Callable[[B], Either[A, C]]
                 ) -> Either[A, C]:
        return f(fa.value) if isinstance(fa, Right) else fa


class EitherOptional(Optional):

    @tc_prop
    def to_maybe(self, fa: Either):
        return maybe.Just(fa.value) if fa.is_right else maybe.Empty()

    def to_either(self, fa: Either, left):
        return fa

__all__ = ('Either', 'Left', 'Right')
