from typing import TypeVar, Callable, Tuple

from amino.tc.base import tc_prop, ImplicitInstances
from amino.tc.optional import Optional
from amino.tc.monad import Monad
from amino.tc.traverse import Traverse
from amino.lazy import lazy
from amino.maybe import Just, Empty
from amino.either import Right, Either, Left
from amino.tc.applicative import Applicative
from amino.tc.foldable import Foldable
from amino import curried

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class EitherInstances(ImplicitInstances):

    @lazy
    def _instances(self):
        from amino.map import Map
        return Map(
            {
                Monad: EitherMonad(),
                Optional: EitherOptional(),
                Traverse: EitherTraverse(),
                Foldable: EitherFoldable(),
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


class EitherFoldable(Foldable):

    @tc_prop
    def with_index(self, fa: Either[A, B]) -> Either[A, Tuple[int, B]]:
        return Right(0) & fa

    def filter(self, fa: Either[A, B], f: Callable[[B], bool]):
        return fa // (lambda a: Right(a) if f(a) else Left('filtered'))

    @curried
    def fold_left(self, fa: Either[A, B], z: C, f: Callable[[C, B], C]) -> C:
        return fa / (lambda a: f(z, a)) | z

    def find(self, fa: Either[A, B], f: Callable[[B], bool]):
        return fa.to_maybe.find(f)

    def find_map(self, fa: Either[A, B], f: Callable[[B], Either[A, C]]
                 ) -> Either[A, C]:
        return fa // f

    def index_where(self, fa: Either[A, B], f: Callable[[B], bool]):
        return fa.to_maybe.index_where(f)

__all__ = ('EitherInstances',)
