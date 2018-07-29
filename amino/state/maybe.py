from typing import Generic, TypeVar, Callable, Tuple, cast, Type, Any

from lenses import UnboundLens

from amino.tc.base import ImplicitsMeta, Implicits
from amino.tc.monad import Monad
from amino.tc.zip import Zip
from amino.instances.list import ListTraverse
from amino import List, curried
from amino.util.string import ToStr
from amino.state.base import StateT
from amino.maybe import Maybe



A = TypeVar('A')
B = TypeVar('B')
S = TypeVar('S')
R = TypeVar('R')
ST1 = TypeVar('ST1')


monad: Monad = cast(Monad, Monad.fatal(Maybe))


class MaybeStateCtor(Generic[S]):

    def inspect(self, f: Callable[[S], A]) -> 'MaybeState[S, A]':
        def g(s: S) -> Maybe[Tuple[S, A]]:
            return monad.pure((s, f(s)))
        return MaybeState.apply(g)

    def inspect_f(self, f: Callable[[S], Maybe[A]]) -> 'MaybeState[S, A]':
        def g(s: S) -> Maybe[Tuple[S, A]]:
            return f(s).map(lambda a: (s, a))
        return MaybeState.apply(g)

    def pure(self, a: A) -> 'MaybeState[S, A]':
        return MaybeState.apply(lambda s: monad.pure((s, a)))

    def delay(self, fa: Callable[..., A], *a: Any, **kw: Any) -> 'MaybeState[S, A]':
        return MaybeState.apply(lambda s: monad.pure((s, fa(*a, **kw))))

    def lift(self, fa: Maybe[A]) -> 'MaybeState[S, A]':
        def g(s: S) -> Maybe[Tuple[S, A]]:
            return fa.map(lambda a: (s, a))
        return MaybeState.apply(g)

    def modify(self, f: Callable[[S], S]) -> 'MaybeState[S, None]':
        return MaybeState.apply(lambda s: monad.pure((f(s), None)))

    def modify_f(self, f: Callable[[S], Maybe[S]]) -> 'MaybeState[S, None]':
        return MaybeState.apply(lambda s: f(s).map(lambda a: (a, None)))

    def get(self) -> 'MaybeState[S, S]':
        return self.inspect(lambda a: a)

    @property
    def unit(self) -> 'MaybeState[S, None]':
        return MaybeState.pure(None)



class MaybeStateMeta(ImplicitsMeta):

    def cons(self, run_f: Maybe[Callable[[S], Maybe[Tuple[S, A]]]]) -> 'MaybeState[S, A]':
        return self(run_f)

    def apply(self, f: Callable[[S], Maybe[Tuple[S, A]]]) -> 'MaybeState[S, A]':
        return self.cons(monad.pure(f))

    def apply_f(self, run_f: Maybe[Callable[[S], Maybe[Tuple[S, A]]]]) -> 'MaybeState[S, A]':
        return self.cons(run_f)

    def inspect(self, f: Callable[[S], A]) -> 'MaybeState[S, A]':
        def g(s: S) -> Maybe[Tuple[S, A]]:
            return monad.pure((s, f(s)))
        return self.apply(g)

    def inspect_f(self, f: Callable[[S], Maybe[A]]) -> 'MaybeState[S, A]':
        def g(s: S) -> Maybe[Tuple[S, A]]:
            return f(s).map(lambda a: (s, a))
        return self.apply(g)

    def pure(self, a: A) -> 'MaybeState[S, A]':
        return self.apply(lambda s: monad.pure((s, a)))

    def reset(self, s: S, a: A) -> 'MaybeState[S, A]':
        return self.apply(lambda _: monad.pure((s, a)))

    def reset_t(self, t: Tuple[S, A]) -> 'MaybeState[S, A]':
        return self.apply(lambda _: monad.pure(t))

    def delay(self, fa: Callable[..., A], *a: Any, **kw: Any) -> 'MaybeState[S, A]':
        return self.apply(lambda s: monad.pure((s, fa(*a, **kw))))

    def lift(self, fa: Maybe[A]) -> 'MaybeState[S, A]':
        def g(s: S) -> Maybe[Tuple[S, A]]:
            return fa.map(lambda a: (s, a))
        return self.apply(g)

    def modify(self, f: Callable[[S], S]) -> 'MaybeState[S, None]':
        return self.apply(lambda s: monad.pure((f(s), None)))

    def modify_f(self, f: Callable[[S], Maybe[S]]) -> 'MaybeState[S, None]':
        return self.apply(lambda s: f(s).map(lambda a: (a, None)))

    def set(self, s: S) -> 'MaybeState[S, None]':
        return self.modify(lambda s0: s)

    def get(self) -> 'MaybeState[S, S]':
        return self.inspect(lambda a: a)

    @property
    def unit(self) -> 'MaybeState[S, None]':
        return MaybeState.pure(None)

    def s(self, tpe: Type[S]) -> MaybeStateCtor[S]:
        return MaybeStateCtor()



class MaybeState(Generic[S, A], StateT, ToStr, Implicits, implicits=True, auto=True, metaclass=MaybeStateMeta):

    def __init__(self, run_f: Maybe[Callable[[S], Maybe[Tuple[S, A]]]]) -> None:
        self.run_f = run_f

    @property
    def cls(self) -> Type['MaybeState[S, A]']:
        return type(self)

    def run(self, s: S) -> Maybe[Tuple[S, A]]:
        return self.run_f.flat_map(lambda f: f(s))

    def run_s(self, s: S) -> Maybe[S]:
        return self.run(s).map(lambda a: a[0])

    def run_a(self, s: S) -> Maybe[S]:
        return self.run(s).map(lambda a: a[1])

    def _arg_desc(self) -> List[str]:
        return List(str(self.run_f))

    def flat_map_f(self, f: Callable[[A], Maybe[B]]) -> 'MaybeState[S, B]':
        def h(s: S, a: A) -> Maybe[Tuple[S, B]]:
            return f(a).map(lambda b: (s, b))
        def g(fsa: Maybe[Tuple[S, A]]) -> Maybe[Tuple[S, B]]:
            return fsa.flat_map2(h)
        run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
        return self.cls.apply_f(run_f1)

    def transform(self, f: Callable[[Tuple[S, A]], Tuple[S, B]]) -> 'MaybeState[S, B]':
        def g(fsa: Maybe[Tuple[S, A]]) -> Maybe[Tuple[S, B]]:
            return fsa.map2(f)
        run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
        return self.cls.apply_f(run_f1)

    def transform_s(self, f: Callable[[R], S], g: Callable[[R, S], R]) -> 'MaybeState[R, A]':
        def trans(sfsa: Callable[[S], Maybe[Tuple[S, A]]], r: R) -> Maybe[Tuple[R, A]]:
            s = f(r)
            return sfsa(s).map2(lambda s, a: (g(r, s), a))
        return self.cls.apply_f(self.run_f.map(curried(trans)))

    def transform_f(self, tpe: Type[ST1], f: Callable[[Maybe[Tuple[S, A]]], Any]) -> ST1:
        def trans(s: S) -> Any:
            return f(self.run(s))
        return tpe.apply(trans)  # type: ignore

    def zoom(self, l: UnboundLens) -> 'MaybeState[R, A]':
        return self.transform_s(l.get(), lambda r, s: l.set(s)(r))

    transform_s_lens = zoom

    def read_zoom(self, l: UnboundLens) -> 'MaybeState[R, A]':
        return self.transform_s(l.get(), lambda r, s: r)

    transform_s_lens_read = read_zoom

    def flat_map(self, f: Callable[[A], 'MaybeState[S, B]']) -> 'MaybeState[S, B]':
        return Monad_MaybeState.flat_map(self, f)


def run_function(s: MaybeState[S, A]) -> Maybe[Callable[[S], Maybe[Tuple[S, A]]]]:
    try:
        return s.run_f
    except Exception as e:
        if not isinstance(s, MaybeState):
            raise TypeError(f'flatMapped {s} into MaybeState')
        else:
            raise


class MaybeStateMonad(Monad, tpe=MaybeState):

    def pure(self, a: A) -> MaybeState[S, A]:  # type: ignore
        return MaybeState.pure(a)

    def flat_map(  # type: ignore
            self,
            fa: MaybeState[S, A],
            f: Callable[[A], MaybeState[S, B]]
    ) -> MaybeState[S, B]:
        def h(s: S, a: A) -> Maybe[Tuple[S, B]]:
            return f(a).run(s)
        def g(fsa: Maybe[Tuple[S, A]]) -> Maybe[Tuple[S, B]]:
            return fsa.flat_map2(h)
        def i(sfsa: Callable[[S], Maybe[Tuple[S, A]]]) -> Callable[[S], Maybe[Tuple[S, B]]]:
            return lambda a: g(sfsa(a))
        run_f1 = run_function(fa).map(i)
        return MaybeState.apply_f(run_f1)


Monad_MaybeState = MaybeStateMonad()


class MaybeStateZip(Zip, tpe=MaybeState):

    def zip(
            self,
            fa: MaybeState[S, A],
            fb: MaybeState[S, A],
            *fs: MaybeState[S, A],
    ) -> MaybeState[S, List[A]]:
        v = ListTraverse().sequence(List(fa, fb, *fs), MaybeState)  # type: ignore
        return cast(MaybeState[S, List[A]], v)



__all__ = ('MaybeState',)
