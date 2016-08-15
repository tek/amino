from typing import TypeVar, Callable

from tryp.tc.base import tc_prop, ImplicitInstances
from tryp.tc.optional import Optional
from tryp.tc.monad import Monad
from tryp.tc.traverse import Traverse
from tryp.lazy import lazy
from tryp.maybe import Just, Empty
from tryp.either import Right, Either, Left
from tryp.tc.applicative import Applicative

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class EitherInstances(ImplicitInstances):

    @lazy
    def _instances(self):
        from tryp.map import Map
        return Map(
            {
                Monad: EitherMonad(),
                Optional: EitherOptional(),
                Traverse: EitherTraverse(),
            }
        )


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

    def to_either(self, fa: Either, left):
        return fa

    @tc_prop
    def present(self, fa: Either):
        return fa.is_right


class EitherTraverse(Traverse):

    def traverse(self, fa: Either[A, B], f: Callable, tpe: type):
        monad = Applicative[tpe]
        r = lambda a: monad.map(f(a), Right)
        return fa.cata(lambda a: monad.pure(Left(a)), r)

__all__ = ('EitherInstances',)
