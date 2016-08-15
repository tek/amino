from typing import TypeVar, Callable, Union
from typing import Tuple  # NOQA

from tryp.tc.base import tc_prop, ImplicitInstances
from tryp.tc.monad import Monad
from tryp.tc.optional import Optional
from tryp import either, Just, Empty, Maybe
from tryp.lazy import lazy
from tryp.maybe import call_by_name
from tryp.tc.applicative import Applicative
from tryp.tc.traverse import Traverse

A = TypeVar('A')
B = TypeVar('B')


class MaybeInstances(ImplicitInstances):

    @lazy
    def _instances(self):
        from tryp import Map
        return Map(
            {
                Monad: MaybeMonad(),
                Optional: MaybeOptional(),
                Traverse: MaybeTraverse(),
            }
        )


class MaybeMonad(Monad):

    def pure(self, a: A):
        return Just(a)

    def flat_map(self, fa: Maybe[A], f: Callable[[A], Maybe[B]]) -> Maybe[B]:
        return fa.cata(lambda v: f(v), Empty())


class MaybeOptional(Optional):

    @tc_prop
    def to_maybe(self, fa: Maybe[A]):
        return fa

    def to_either(self, fa: Maybe[A], left: Union[B, Callable[[], B]]
                  ) -> either.Either[A, B]:
        from tryp.either import Left, Right
        return fa.cata(Right, lambda: Left(call_by_name(left)))

    @tc_prop
    def present(self, fa: Maybe):
        return fa.is_just


class MaybeTraverse(Traverse):

    def traverse(self, fa: Maybe[A], f: Callable, tpe: type):
        monad = Applicative[tpe]
        r = lambda a: monad.map(f(a), Just)
        return fa.cata(r, monad.pure(Empty()))

__all__ = ('MaybeInstances',)
