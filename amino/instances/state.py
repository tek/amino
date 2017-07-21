from typing import TypeVar, Callable

from amino.tc.base import ImplicitInstances
from amino.tc.monad import Monad
from amino.lazy import lazy
from amino.state import State, StateF
from amino import Map

S = TypeVar('S')
A = TypeVar('A')
B = TypeVar('B')


class StateInstances(ImplicitInstances):

    @lazy
    def _instances(self) -> Map:
        return Map(
            {
                Monad: StateMonad(),
            }
        )


class StateMonad(Monad):

    def pure(self, a: A) -> State[S, A]:
        return self.pureF(a, StateF)

    def pureF(self, a: A, tpe: type) -> State[S, A]:
        return State.pure(a, tpe)

    def flat_map(self, fa: State[S, A], f: Callable[[A], State[S, B]]) -> State[S, B]:
        def h(s: S, a: A) -> None:
            return f(a).run(s)
        def g(fsa) -> None:
            return fa._flat_map.flat_map2(fsa, h)
        run_f1 = fa._flat_map.map(fa.run_f, lambda sfsa: lambda a: g(sfsa(a)))
        return State.applyF(run_f1)

__all__ = ('StateMonad', 'StateInstances')
