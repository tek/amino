from typing import Generic, TypeVar, Callable, Tuple

from amino.tc.applicative import Applicative
from amino.tc.base import Implicits
from amino.lazy import lazy
from amino.tc.flat_map import FlatMap
from amino.tc.monad import Monad

S = TypeVar('S')
A = TypeVar('A')
B = TypeVar('B')


class StateF(Generic[A], Implicits, auto=True):

    def __init__(self, a: A) -> None:
        self.a = a

F = StateF


class StateFMonad(Monad, tpe=F):

    def pure(a: A) -> StateF[A]:
        return StateF(a)

    def flat_map(self, fa: F[A], f: Callable[[A], F[B]]) -> F[B]:
        return f(fa.a)


class StateFunctions:

    @staticmethod
    def apply(f: Callable[[S], F[Tuple[S, A]]], tpe: type) -> 'State[S, A]':
        return State(Applicative.fatal(tpe).pure(f))

    @staticmethod
    def applyF(run_f: F[Callable[[S], F[Tuple[S, A]]]]) -> 'State[S, A]':
        return State(run_f)

    @staticmethod
    def inspect(f: Callable[[S], A], tpe: type) -> 'State[S, A]':
        def g(s: S) -> F[Tuple[S, A]]:
            return Applicative.fatal(tpe).pure((s, f(s)))
        return State.apply(g, tpe)

    @staticmethod
    def pure(a: A, tpe: type) -> 'State[S, A]':
        app = Applicative.fatal(tpe)
        return State(app.pure(lambda s: app.pure((s, a))))

    @staticmethod
    def modify(f: Callable[[S], S], tpe: type) -> 'State[S, A]':
        return State.apply(lambda s: Applicative.fatal(tpe).pure((f(s), None)), tpe)


class State(Generic[S, A], Implicits, StateFunctions, implicits=True):

    def __init__(self, run_f: F[Callable[[S], F[Tuple[S, A]]]]) -> None:
        self.tpe = type(run_f)
        self.run_f = run_f

    @lazy
    def _applicative(self) -> Applicative[F]:
        return Applicative.fatal(self.tpe)

    @lazy
    def _flat_map(self) -> Applicative[F]:
        return FlatMap.fatal(self.tpe)

    def run(self, s: S) -> F[Tuple[S, A]]:
        return self.run_f.flat_map(lambda f: f(s))

    def run_s(self, s: S) -> F[S]:
        return self.run(s).map(lambda a: a[0])

    def __str__(self) -> str:
        return f'State({self.run_f})'

    def flat_map_f(self, f: Callable[[A], F[B]]) -> 'State[S, B]':
        def h(s: S, a: A) -> F[Tuple[S, B]]:
            return f(a).map(lambda b: (s, b))
        def g(fsa: F[Tuple[S, A]]) -> F[Tuple[S, B]]:
            return fsa.flat_map2(h)
        run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
        return State.applyF(run_f1)

__all__ = ('State',)
