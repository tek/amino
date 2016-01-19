from typing import TypeVar, Generic, Callable, Union  # type: ignore
import abc

from tryp import Empty, Just, Map
from tryp.typeclass import Implicits, tc_prop
from tryp.tc.functor import Functor
from tryp.typeclass import ImplicitInstances
from tryp.lazy import lazy
from tryp.tc.optional import Optional

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class EitherInstances(ImplicitInstances):

    @lazy
    def _instances(self):
        return Map({Functor: EitherFunctor(), Optional: EitherOptional()})


class Either(Generic[A, B], Implicits, implicits=True):

    def __init__(self, value: Union[A, B]):
        self.value = value

    @property
    def is_right(self):
        return isinstance(self, Right)

    @property
    def is_left(self):
        return isinstance(self, Left)


class Right(Either):
    pass


class Left(Either):
    pass


class EitherFunctor(Functor):

    def map(self, fa: Either[A, B], f: Callable[[B], C]) -> Either[A, C]:
        return Right(f(fa.value)) if isinstance(fa, Right) else fa


class EitherOptional(Optional):

    @tc_prop
    def to_maybe(self, fa: Either):
        return Just(fa.value) if fa.is_right else Empty()

__all__ = ['Either', 'Left', 'Right']
