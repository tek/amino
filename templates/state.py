from typing import Generic, TypeVar, Callable, Tuple, cast, Type, Any

from lenses import UnboundLens

from amino.tc.base import ImplicitsMeta, Implicits
from amino.tc.monad import Monad
from amino.tc.zip import Zip
from amino.instances.list import ListTraverse
from amino import List, curried
from amino.util.string import ToStr
from amino.state.base import StateBase
{f_import}

{extra_import}

A = TypeVar('A')
B = TypeVar('B')
S = TypeVar('S')
R = TypeVar('R')
ST1 = TypeVar('ST1')
{tvar}

monad: Monad = cast(Monad, Monad.fatal(F))


class StateTCtor(Generic[S]):

    def inspect(self, f: Callable[[S], A]) -> 'StateT[S, A]':
        def g(s: S) -> F[Tuple[S, A]]:
            return monad.pure((s, f(s)))
        return StateT.apply(g)

    def inspect_f(self, f: Callable[[S], F[A]]) -> 'StateT[S, A]':
        def g(s: S) -> F[Tuple[S, A]]:
            return f(s).map(lambda a: (s, a))
        return StateT.apply(g)

    def pure(self, a: A) -> 'StateT[S, A]':
        return StateT.apply(lambda s: monad.pure((s, a)))

    def delay(self, fa: Callable[..., A], *a: Any, **kw: Any) -> 'StateT[S, A]':
        return StateT.apply(lambda s: monad.pure((s, fa(*a, **kw))))

    def lift(self, fa: F[A]) -> 'StateT[S, A]':
        def g(s: S) -> F[Tuple[S, A]]:
            return fa.map(lambda a: (s, a))
        return StateT.apply(g)

    def modify(self, f: Callable[[S], S]) -> 'StateT[S, None]':
        return StateT.apply(lambda s: monad.pure((f(s), None)))

    def modify_f(self, f: Callable[[S], F[S]]) -> 'StateT[S, None]':
        return StateT.apply(lambda s: f(s).map(lambda a: (a, None)))

    def get(self) -> 'StateT[S, S]':
        return self.inspect(lambda a: a)

    @property
    def unit(self) -> 'StateT[S, None]':
        return StateT.pure(None)

{ctor_extra}

class StateTMeta(ImplicitsMeta):

    def cons(self, run_f: F[Callable[[S], F[Tuple[S, A]]]]) -> 'StateT[S, A]':
        return self(run_f)

    def apply(self, f: Callable[[S], F[Tuple[S, A]]]) -> 'StateT[S, A]':
        return self.cons(monad.pure(f))

    def apply_f(self, run_f: F[Callable[[S], F[Tuple[S, A]]]]) -> 'StateT[S, A]':
        return self.cons(run_f)

    def inspect(self, f: Callable[[S], A]) -> 'StateT[S, A]':
        def g(s: S) -> F[Tuple[S, A]]:
            return monad.pure((s, f(s)))
        return self.apply(g)

    def inspect_f(self, f: Callable[[S], F[A]]) -> 'StateT[S, A]':
        def g(s: S) -> F[Tuple[S, A]]:
            return f(s).map(lambda a: (s, a))
        return self.apply(g)

    def pure(self, a: A) -> 'StateT[S, A]':
        return self.apply(lambda s: monad.pure((s, a)))

    def reset(self, s: S, a: A) -> 'StateT[S, A]':
        return self.apply(lambda _: monad.pure((s, a)))

    def reset_t(self, t: Tuple[S, A]) -> 'StateT[S, A]':
        return self.apply(lambda _: monad.pure(t))

    def delay(self, fa: Callable[..., A], *a: Any, **kw: Any) -> 'StateT[S, A]':
        return self.apply(lambda s: monad.pure((s, fa(*a, **kw))))

    def lift(self, fa: F[A]) -> 'StateT[S, A]':
        def g(s: S) -> F[Tuple[S, A]]:
            return fa.map(lambda a: (s, a))
        return self.apply(g)

    def modify(self, f: Callable[[S], S]) -> 'StateT[S, None]':
        return self.apply(lambda s: monad.pure((f(s), None)))

    def modify_f(self, f: Callable[[S], F[S]]) -> 'StateT[S, None]':
        return self.apply(lambda s: f(s).map(lambda a: (a, None)))

    def set(self, s: S) -> 'StateT[S, None]':
        return self.modify(lambda s0: s)

    def get(self) -> 'StateT[S, S]':
        return self.inspect(lambda a: a)

    @property
    def unit(self) -> 'StateT[S, None]':
        return StateT.pure(None)

    def s(self, tpe: Type[S]) -> StateTCtor[S]:
        return StateTCtor()

{meta_extra}

class StateT(Generic[{tpar}S, A], StateBase, ToStr, Implicits, implicits=True, auto=True, metaclass=StateTMeta):

    def __init__(self, run_f: F[Callable[[S], F[Tuple[S, A]]]]) -> None:
        self.run_f = run_f

    @property
    def cls(self) -> Type['StateT[S, A]']:
        return type(self)

    def run(self, s: S) -> F[Tuple[S, A]]:
        return self.run_f.flat_map(lambda f: f(s))

    def run_s(self, s: S) -> F[S]:
        return self.run(s).map(lambda a: a[0])

    def run_a(self, s: S) -> F[S]:
        return self.run(s).map(lambda a: a[1])

    def _arg_desc(self) -> List[str]:
        return List(str(self.run_f))

    def flat_map_f(self, f: Callable[[A], F[B]]) -> 'StateT[S, B]':
        def h(s: S, a: A) -> F[Tuple[S, B]]:
            return f(a).map(lambda b: (s, b))
        def g(fsa: F[Tuple[S, A]]) -> F[Tuple[S, B]]:
            return fsa.flat_map2(h)
        run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
        return self.cls.apply_f(run_f1)

    def transform(self, f: Callable[[Tuple[S, A]], Tuple[S, B]]) -> 'StateT[S, B]':
        def g(fsa: F[Tuple[S, A]]) -> F[Tuple[S, B]]:
            return fsa.map2(f)
        run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
        return self.cls.apply_f(run_f1)

    def transform_s(self, f: Callable[[R], S], g: Callable[[R, S], R]) -> 'StateT[R, A]':
        def trans(sfsa: Callable[[S], F[Tuple[S, A]]], r: R) -> F[Tuple[R, A]]:
            s = f(r)
            return sfsa(s).map2(lambda s, a: (g(r, s), a))
        return self.cls.apply_f(self.run_f.map(curried(trans)))

    def transform_f(self, tpe: Type[ST1], f: Callable[[F[Tuple[S, A]]], Any]) -> ST1:
        def trans(s: S) -> Any:
            return f(self.run(s))
        return tpe.apply(trans)  # type: ignore

    def zoom(self, l: UnboundLens) -> 'StateT[R, A]':
        return self.transform_s(l.get(), lambda r, s: l.set(s)(r))

    transform_s_lens = zoom

    def read_zoom(self, l: UnboundLens) -> 'StateT[R, A]':
        return self.transform_s(l.get(), lambda r, s: r)

    transform_s_lens_read = read_zoom

    def flat_map(self, f: Callable[[A], 'StateT[S, B]']) -> 'StateT[S, B]':
        return Monad_StateT.flat_map(self, f)

{class_extra}
def run_function(s: StateT[S, A]) -> F[Callable[[S], F[Tuple[S, A]]]]:
    try:
        return s.run_f
    except Exception as e:
        if not isinstance(s, StateT):
            raise TypeError(f'flatMapped {s} into StateT')
        else:
            raise


class StateTMonad(Monad, tpe=StateT):

    def pure(self, a: A) -> StateT[S, A]:  # type: ignore
        return StateT.pure(a)

    def flat_map(  # type: ignore
            self,
            fa: StateT[S, A],
            f: Callable[[A], StateT[S, B]]
    ) -> StateT[S, B]:
        def h(s: S, a: A) -> F[Tuple[S, B]]:
            return f(a).run(s)
        def g(fsa: F[Tuple[S, A]]) -> F[Tuple[S, B]]:
            return fsa.flat_map2(h)
        def i(sfsa: Callable[[S], F[Tuple[S, A]]]) -> Callable[[S], F[Tuple[S, B]]]:
            return lambda a: g(sfsa(a))
        run_f1 = run_function(fa).map(i)
        return StateT.apply_f(run_f1)


Monad_StateT = StateTMonad()


class StateTZip(Zip, tpe=StateT):

    def zip(
            self,
            fa: StateT[S, A],
            fb: StateT[S, A],
            *fs: StateT[S, A],
    ) -> StateT[S, List[A]]:
        v = ListTraverse().sequence(List(fa, fb, *fs), StateT)  # type: ignore
        return cast(StateT[S, List[A]], v)

{extra}

__all__ = ('StateT',)
