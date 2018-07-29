from typing import Generic, TypeVar, Callable, Tuple, cast, Type, Any

from lenses import UnboundLens

from amino.tc.base import ImplicitsMeta, Implicits
from amino.tc.monad import Monad
from amino.tc.zip import Zip
from amino.instances.list import ListTraverse
from amino import List, curried
from amino.util.string import ToStr
from amino.state.base import StateT
from amino.either import Either



A = TypeVar('A')
B = TypeVar('B')
S = TypeVar('S')
R = TypeVar('R')
ST1 = TypeVar('ST1')
E = TypeVar('E')

monad: Monad = cast(Monad, Monad.fatal(Either))


class EitherStateCtor(Generic[S]):

    def inspect(self, f: Callable[[S], A]) -> 'EitherState[E, S, A]':
        def g(s: S) -> Either[E, Tuple[S, A]]:
            return monad.pure((s, f(s)))
        return EitherState.apply(g)

    def inspect_f(self, f: Callable[[S], Either[E, A]]) -> 'EitherState[E, S, A]':
        def g(s: S) -> Either[E, Tuple[S, A]]:
            return f(s).map(lambda a: (s, a))
        return EitherState.apply(g)

    def pure(self, a: A) -> 'EitherState[E, S, A]':
        return EitherState.apply(lambda s: monad.pure((s, a)))

    def delay(self, fa: Callable[..., A], *a: Any, **kw: Any) -> 'EitherState[E, S, A]':
        return EitherState.apply(lambda s: monad.pure((s, fa(*a, **kw))))

    def lift(self, fa: Either[E, A]) -> 'EitherState[E, S, A]':
        def g(s: S) -> Either[E, Tuple[S, A]]:
            return fa.map(lambda a: (s, a))
        return EitherState.apply(g)

    def modify(self, f: Callable[[S], S]) -> 'EitherState[E, S, None]':
        return EitherState.apply(lambda s: monad.pure((f(s), None)))

    def modify_f(self, f: Callable[[S], Either[E, S]]) -> 'EitherState[E, S, None]':
        return EitherState.apply(lambda s: f(s).map(lambda a: (a, None)))

    def get(self) -> 'EitherState[E, S, S]':
        return self.inspect(lambda a: a)

    @property
    def unit(self) -> 'EitherState[E, S, None]':
        return EitherState.pure(None)



class EitherStateMeta(ImplicitsMeta):

    def cons(self, run_f: Either[E, Callable[[S], Either[E, Tuple[S, A]]]]) -> 'EitherState[E, S, A]':
        return self(run_f)

    def apply(self, f: Callable[[S], Either[E, Tuple[S, A]]]) -> 'EitherState[E, S, A]':
        return self.cons(monad.pure(f))

    def apply_f(self, run_f: Either[E, Callable[[S], Either[E, Tuple[S, A]]]]) -> 'EitherState[E, S, A]':
        return self.cons(run_f)

    def inspect(self, f: Callable[[S], A]) -> 'EitherState[E, S, A]':
        def g(s: S) -> Either[E, Tuple[S, A]]:
            return monad.pure((s, f(s)))
        return self.apply(g)

    def inspect_f(self, f: Callable[[S], Either[E, A]]) -> 'EitherState[E, S, A]':
        def g(s: S) -> Either[E, Tuple[S, A]]:
            return f(s).map(lambda a: (s, a))
        return self.apply(g)

    def pure(self, a: A) -> 'EitherState[E, S, A]':
        return self.apply(lambda s: monad.pure((s, a)))

    def reset(self, s: S, a: A) -> 'EitherState[E, S, A]':
        return self.apply(lambda _: monad.pure((s, a)))

    def reset_t(self, t: Tuple[S, A]) -> 'EitherState[E, S, A]':
        return self.apply(lambda _: monad.pure(t))

    def delay(self, fa: Callable[..., A], *a: Any, **kw: Any) -> 'EitherState[E, S, A]':
        return self.apply(lambda s: monad.pure((s, fa(*a, **kw))))

    def lift(self, fa: Either[E, A]) -> 'EitherState[E, S, A]':
        def g(s: S) -> Either[E, Tuple[S, A]]:
            return fa.map(lambda a: (s, a))
        return self.apply(g)

    def modify(self, f: Callable[[S], S]) -> 'EitherState[E, S, None]':
        return self.apply(lambda s: monad.pure((f(s), None)))

    def modify_f(self, f: Callable[[S], Either[E, S]]) -> 'EitherState[E, S, None]':
        return self.apply(lambda s: f(s).map(lambda a: (a, None)))

    def set(self, s: S) -> 'EitherState[E, S, None]':
        return self.modify(lambda s0: s)

    def get(self) -> 'EitherState[E, S, S]':
        return self.inspect(lambda a: a)

    @property
    def unit(self) -> 'EitherState[E, S, None]':
        return EitherState.pure(None)

    def s(self, tpe: Type[S]) -> EitherStateCtor[S]:
        return EitherStateCtor()



class EitherState(Generic[E, S, A], StateT, ToStr, Implicits, implicits=True, auto=True, metaclass=EitherStateMeta):

    def __init__(self, run_f: Either[E, Callable[[S], Either[E, Tuple[S, A]]]]) -> None:
        self.run_f = run_f

    @property
    def cls(self) -> Type['EitherState[E, S, A]']:
        return type(self)

    def run(self, s: S) -> Either[E, Tuple[S, A]]:
        return self.run_f.flat_map(lambda f: f(s))

    def run_s(self, s: S) -> Either[E, S]:
        return self.run(s).map(lambda a: a[0])

    def run_a(self, s: S) -> Either[E, S]:
        return self.run(s).map(lambda a: a[1])

    def _arg_desc(self) -> List[str]:
        return List(str(self.run_f))

    def flat_map_f(self, f: Callable[[A], Either[E, B]]) -> 'EitherState[E, S, B]':
        def h(s: S, a: A) -> Either[E, Tuple[S, B]]:
            return f(a).map(lambda b: (s, b))
        def g(fsa: Either[E, Tuple[S, A]]) -> Either[E, Tuple[S, B]]:
            return fsa.flat_map2(h)
        run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
        return self.cls.apply_f(run_f1)

    def transform(self, f: Callable[[Tuple[S, A]], Tuple[S, B]]) -> 'EitherState[E, S, B]':
        def g(fsa: Either[E, Tuple[S, A]]) -> Either[E, Tuple[S, B]]:
            return fsa.map2(f)
        run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
        return self.cls.apply_f(run_f1)

    def transform_s(self, f: Callable[[R], S], g: Callable[[R, S], R]) -> 'EitherState[E, R, A]':
        def trans(sfsa: Callable[[S], Either[E, Tuple[S, A]]], r: R) -> Either[E, Tuple[R, A]]:
            s = f(r)
            return sfsa(s).map2(lambda s, a: (g(r, s), a))
        return self.cls.apply_f(self.run_f.map(curried(trans)))

    def transform_f(self, tpe: Type[ST1], f: Callable[[Either[E, Tuple[S, A]]], Any]) -> ST1:
        def trans(s: S) -> Any:
            return f(self.run(s))
        return tpe.apply(trans)  # type: ignore

    def zoom(self, l: UnboundLens) -> 'EitherState[E, R, A]':
        return self.transform_s(l.get(), lambda r, s: l.set(s)(r))

    transform_s_lens = zoom

    def read_zoom(self, l: UnboundLens) -> 'EitherState[E, R, A]':
        return self.transform_s(l.get(), lambda r, s: r)

    transform_s_lens_read = read_zoom

    def flat_map(self, f: Callable[[A], 'EitherState[E, S, B]']) -> 'EitherState[E, S, B]':
        return Monad_EitherState.flat_map(self, f)


def run_function(s: EitherState[E, S, A]) -> Either[E, Callable[[S], Either[E, Tuple[S, A]]]]:
    try:
        return s.run_f
    except Exception as e:
        if not isinstance(s, EitherState):
            raise TypeError(f'flatMapped {s} into EitherState')
        else:
            raise


class EitherStateMonad(Monad, tpe=EitherState):

    def pure(self, a: A) -> EitherState[E, S, A]:  # type: ignore
        return EitherState.pure(a)

    def flat_map(  # type: ignore
            self,
            fa: EitherState[E, S, A],
            f: Callable[[A], EitherState[E, S, B]]
    ) -> EitherState[E, S, B]:
        def h(s: S, a: A) -> Either[E, Tuple[S, B]]:
            return f(a).run(s)
        def g(fsa: Either[E, Tuple[S, A]]) -> Either[E, Tuple[S, B]]:
            return fsa.flat_map2(h)
        def i(sfsa: Callable[[S], Either[E, Tuple[S, A]]]) -> Callable[[S], Either[E, Tuple[S, B]]]:
            return lambda a: g(sfsa(a))
        run_f1 = run_function(fa).map(i)
        return EitherState.apply_f(run_f1)


Monad_EitherState = EitherStateMonad()


class EitherStateZip(Zip, tpe=EitherState):

    def zip(
            self,
            fa: EitherState[E, S, A],
            fb: EitherState[E, S, A],
            *fs: EitherState[E, S, A],
    ) -> EitherState[E, S, List[A]]:
        v = ListTraverse().sequence(List(fa, fb, *fs), EitherState)  # type: ignore
        return cast(EitherState[E, S, List[A]], v)



__all__ = ('EitherState',)
