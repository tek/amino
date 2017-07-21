import abc
from typing import Generic, TypeVar, Callable, Tuple, GenericMeta

from amino.tc.base import Implicits
from amino.tc.monad import Monad
from amino.tc.zip import Zip
from amino.instances.list import ListTraverse
from amino import List

S = TypeVar('S')
A = TypeVar('A')
B = TypeVar('B')


class StateTMeta(GenericMeta):
    pass


def StateT(tpe: type) -> type:
    class F(Generic[A], Implicits, abc.ABC):
        pass
    F.register(tpe)
    monad = Monad.fatal(tpe)
    class State(Generic[S, A], Implicits, implicits=True, auto=True):

        @staticmethod
        def apply(f: Callable[[S], F[Tuple[S, A]]]) -> 'State[S, A]':
            return State(monad.pure(f))

        @staticmethod
        def applyF(run_f: F[Callable[[S], F[Tuple[S, A]]]]) -> 'State[S, A]':
            return State(run_f)

        @staticmethod
        def inspect(f: Callable[[S], A]) -> 'State[S, A]':
            def g(s: S) -> F[Tuple[S, A]]:
                return monad.pure((s, f(s)))
            return State.apply(g)

        @staticmethod
        def pure(a: A) -> 'State[S, A]':
            return State(monad.pure(lambda s: monad.pure((s, a))))

        @staticmethod
        def modify(f: Callable[[S], S]) -> 'State[S, A]':
            return State.apply(lambda s: monad.pure((f(s), None)))

        def __init__(self, run_f: F[Callable[[S], F[Tuple[S, A]]]]) -> None:
            self.run_f = run_f

        def run(self, s: S) -> F[Tuple[S, A]]:
            return self.run_f.flat_map(lambda f: f(s))

        def run_s(self, s: S) -> F[S]:
            return self.run(s).map(lambda a: a[0])

        def run_a(self, s: S) -> F[S]:
            return self.run(s).map(lambda a: a[1])

        def __str__(self) -> str:
            return f'State({self.run_f})'

        def flat_map_f(self, f: Callable[[A], F[B]]) -> 'State[S, B]':
            def h(s: S, a: A) -> F[Tuple[S, B]]:
                return f(a).map(lambda b: (s, b))
            def g(fsa: F[Tuple[S, A]]) -> F[Tuple[S, B]]:
                return fsa.flat_map2(h)
            run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
            return State.applyF(run_f1)
    class StateMonad(Monad, tpe=State):

        def pure(self, a: A) -> State[S, A]:
            return State.pure(a)

        def flat_map(self, fa: State[S, A], f: Callable[[A], State[S, B]]) -> State[S, B]:
            def h(s: S, a: A) -> F[Tuple[S, B]]:
                return f(a).run(s)
            def g(fsa: F[Tuple[S, A]]) -> F[Tuple[S, B]]:
                return fsa.flat_map2(h)
            def i(sfsa: Callable[[S], F[Tuple[S, A]]]) -> Callable[[S], F[Tuple[S, B]]]:
                return lambda a: g(sfsa(a))
            run_f1 = fa.run_f.map(i)
            return State.applyF(run_f1)
    class StateZip(Zip, tpe=State):

        def zip(self, fa: State[S, A], fb: State[S, B], *fs: State) -> State[S, List[A]]:
            return ListTraverse().sequence(List(fa, fb, *fs), State)
    return type(f'State_{tpe.__name__}', (State,), {})

__all__ = ('StateT',)
