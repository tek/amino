from typing import Generic, TypeVar, Callable, Tuple, cast, Type, Any

from lenses import UnboundLens

from amino.tc.base import ImplicitsMeta, Implicits
from amino.tc.monad import Monad
from amino.tc.zip import Zip
from amino.instances.list import ListTraverse
from amino import List, curried
from amino.util.string import ToStr
from amino.state.base import StateT
from amino.eval import Eval



A = TypeVar('A')
B = TypeVar('B')
S = TypeVar('S')
R = TypeVar('R')
ST1 = TypeVar('ST1')


monad: Monad = cast(Monad, Monad.fatal(Eval))


class EvalStateCtor(Generic[S]):

    def inspect(self, f: Callable[[S], A]) -> 'EvalState[S, A]':
        def g(s: S) -> Eval[Tuple[S, A]]:
            return monad.pure((s, f(s)))
        return EvalState.apply(g)

    def inspect_f(self, f: Callable[[S], Eval[A]]) -> 'EvalState[S, A]':
        def g(s: S) -> Eval[Tuple[S, A]]:
            return f(s).map(lambda a: (s, a))
        return EvalState.apply(g)

    def pure(self, a: A) -> 'EvalState[S, A]':
        return EvalState.apply(lambda s: monad.pure((s, a)))

    def delay(self, fa: Callable[..., A], *a: Any, **kw: Any) -> 'EvalState[S, A]':
        return EvalState.apply(lambda s: monad.pure((s, fa(*a, **kw))))

    def lift(self, fa: Eval[A]) -> 'EvalState[S, A]':
        def g(s: S) -> Eval[Tuple[S, A]]:
            return fa.map(lambda a: (s, a))
        return EvalState.apply(g)

    def modify(self, f: Callable[[S], S]) -> 'EvalState[S, None]':
        return EvalState.apply(lambda s: monad.pure((f(s), None)))

    def modify_f(self, f: Callable[[S], Eval[S]]) -> 'EvalState[S, None]':
        return EvalState.apply(lambda s: f(s).map(lambda a: (a, None)))

    def get(self) -> 'EvalState[S, S]':
        return self.inspect(lambda a: a)

    @property
    def unit(self) -> 'EvalState[S, None]':
        return EvalState.pure(None)



class EvalStateMeta(ImplicitsMeta):

    def cons(self, run_f: Eval[Callable[[S], Eval[Tuple[S, A]]]]) -> 'EvalState[S, A]':
        return self(run_f)

    def apply(self, f: Callable[[S], Eval[Tuple[S, A]]]) -> 'EvalState[S, A]':
        return self.cons(monad.pure(f))

    def apply_f(self, run_f: Eval[Callable[[S], Eval[Tuple[S, A]]]]) -> 'EvalState[S, A]':
        return self.cons(run_f)

    def inspect(self, f: Callable[[S], A]) -> 'EvalState[S, A]':
        def g(s: S) -> Eval[Tuple[S, A]]:
            return monad.pure((s, f(s)))
        return self.apply(g)

    def inspect_f(self, f: Callable[[S], Eval[A]]) -> 'EvalState[S, A]':
        def g(s: S) -> Eval[Tuple[S, A]]:
            return f(s).map(lambda a: (s, a))
        return self.apply(g)

    def pure(self, a: A) -> 'EvalState[S, A]':
        return self.apply(lambda s: monad.pure((s, a)))

    def reset(self, s: S, a: A) -> 'EvalState[S, A]':
        return self.apply(lambda _: monad.pure((s, a)))

    def reset_t(self, t: Tuple[S, A]) -> 'EvalState[S, A]':
        return self.apply(lambda _: monad.pure(t))

    def delay(self, fa: Callable[..., A], *a: Any, **kw: Any) -> 'EvalState[S, A]':
        return self.apply(lambda s: monad.pure((s, fa(*a, **kw))))

    def lift(self, fa: Eval[A]) -> 'EvalState[S, A]':
        def g(s: S) -> Eval[Tuple[S, A]]:
            return fa.map(lambda a: (s, a))
        return self.apply(g)

    def modify(self, f: Callable[[S], S]) -> 'EvalState[S, None]':
        return self.apply(lambda s: monad.pure((f(s), None)))

    def modify_f(self, f: Callable[[S], Eval[S]]) -> 'EvalState[S, None]':
        return self.apply(lambda s: f(s).map(lambda a: (a, None)))

    def set(self, s: S) -> 'EvalState[S, None]':
        return self.modify(lambda s0: s)

    def get(self) -> 'EvalState[S, S]':
        return self.inspect(lambda a: a)

    @property
    def unit(self) -> 'EvalState[S, None]':
        return EvalState.pure(None)

    def s(self, tpe: Type[S]) -> EvalStateCtor[S]:
        return EvalStateCtor()



class EvalState(Generic[S, A], StateT, ToStr, Implicits, implicits=True, auto=True, metaclass=EvalStateMeta):

    def __init__(self, run_f: Eval[Callable[[S], Eval[Tuple[S, A]]]]) -> None:
        self.run_f = run_f

    @property
    def cls(self) -> Type['EvalState[S, A]']:
        return type(self)

    def run(self, s: S) -> Eval[Tuple[S, A]]:
        return self.run_f.flat_map(lambda f: f(s))

    def run_s(self, s: S) -> Eval[S]:
        return self.run(s).map(lambda a: a[0])

    def run_a(self, s: S) -> Eval[S]:
        return self.run(s).map(lambda a: a[1])

    def _arg_desc(self) -> List[str]:
        return List(str(self.run_f))

    def flat_map_f(self, f: Callable[[A], Eval[B]]) -> 'EvalState[S, B]':
        def h(s: S, a: A) -> Eval[Tuple[S, B]]:
            return f(a).map(lambda b: (s, b))
        def g(fsa: Eval[Tuple[S, A]]) -> Eval[Tuple[S, B]]:
            return fsa.flat_map2(h)
        run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
        return self.cls.apply_f(run_f1)

    def transform(self, f: Callable[[Tuple[S, A]], Tuple[S, B]]) -> 'EvalState[S, B]':
        def g(fsa: Eval[Tuple[S, A]]) -> Eval[Tuple[S, B]]:
            return fsa.map2(f)
        run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
        return self.cls.apply_f(run_f1)

    def transform_s(self, f: Callable[[R], S], g: Callable[[R, S], R]) -> 'EvalState[R, A]':
        def trans(sfsa: Callable[[S], Eval[Tuple[S, A]]], r: R) -> Eval[Tuple[R, A]]:
            s = f(r)
            return sfsa(s).map2(lambda s, a: (g(r, s), a))
        return self.cls.apply_f(self.run_f.map(curried(trans)))

    def transform_f(self, tpe: Type[ST1], f: Callable[[Eval[Tuple[S, A]]], Any]) -> ST1:
        def trans(s: S) -> Any:
            return f(self.run(s))
        return tpe.apply(trans)  # type: ignore

    def zoom(self, l: UnboundLens) -> 'EvalState[R, A]':
        return self.transform_s(l.get(), lambda r, s: l.set(s)(r))

    transform_s_lens = zoom

    def read_zoom(self, l: UnboundLens) -> 'EvalState[R, A]':
        return self.transform_s(l.get(), lambda r, s: r)

    transform_s_lens_read = read_zoom

    def flat_map(self, f: Callable[[A], 'EvalState[S, B]']) -> 'EvalState[S, B]':
        return Monad_EvalState.flat_map(self, f)


def run_function(s: EvalState[S, A]) -> Eval[Callable[[S], Eval[Tuple[S, A]]]]:
    try:
        return s.run_f
    except Exception as e:
        if not isinstance(s, EvalState):
            raise TypeError(f'flatMapped {s} into EvalState')
        else:
            raise


class EvalStateMonad(Monad, tpe=EvalState):

    def pure(self, a: A) -> EvalState[S, A]:  # type: ignore
        return EvalState.pure(a)

    def flat_map(  # type: ignore
            self,
            fa: EvalState[S, A],
            f: Callable[[A], EvalState[S, B]]
    ) -> EvalState[S, B]:
        def h(s: S, a: A) -> Eval[Tuple[S, B]]:
            return f(a).run(s)
        def g(fsa: Eval[Tuple[S, A]]) -> Eval[Tuple[S, B]]:
            return fsa.flat_map2(h)
        def i(sfsa: Callable[[S], Eval[Tuple[S, A]]]) -> Callable[[S], Eval[Tuple[S, B]]]:
            return lambda a: g(sfsa(a))
        run_f1 = run_function(fa).map(i)
        return EvalState.apply_f(run_f1)


Monad_EvalState = EvalStateMonad()


class EvalStateZip(Zip, tpe=EvalState):

    def zip(
            self,
            fa: EvalState[S, A],
            fb: EvalState[S, A],
            *fs: EvalState[S, A],
    ) -> EvalState[S, List[A]]:
        v = ListTraverse().sequence(List(fa, fb, *fs), EvalState)  # type: ignore
        return cast(EvalState[S, List[A]], v)



__all__ = ('EvalState',)
