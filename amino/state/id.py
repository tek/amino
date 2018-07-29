from typing import Generic, TypeVar, Callable, Tuple, cast, Type, Any

from lenses import UnboundLens

from amino.tc.base import ImplicitsMeta, Implicits
from amino.tc.monad import Monad
from amino.tc.zip import Zip
from amino.instances.list import ListTraverse
from amino import List, curried
from amino.util.string import ToStr
from amino.state.base import StateT
from amino.id import Id



A = TypeVar('A')
B = TypeVar('B')
S = TypeVar('S')
R = TypeVar('R')
ST1 = TypeVar('ST1')


monad: Monad = cast(Monad, Monad.fatal(Id))


class IdStateCtor(Generic[S]):

    def inspect(self, f: Callable[[S], A]) -> 'IdState[S, A]':
        def g(s: S) -> Id[Tuple[S, A]]:
            return monad.pure((s, f(s)))
        return IdState.apply(g)

    def inspect_f(self, f: Callable[[S], Id[A]]) -> 'IdState[S, A]':
        def g(s: S) -> Id[Tuple[S, A]]:
            return f(s).map(lambda a: (s, a))
        return IdState.apply(g)

    def pure(self, a: A) -> 'IdState[S, A]':
        return IdState.apply(lambda s: monad.pure((s, a)))

    def delay(self, fa: Callable[..., A], *a: Any, **kw: Any) -> 'IdState[S, A]':
        return IdState.apply(lambda s: monad.pure((s, fa(*a, **kw))))

    def lift(self, fa: Id[A]) -> 'IdState[S, A]':
        def g(s: S) -> Id[Tuple[S, A]]:
            return fa.map(lambda a: (s, a))
        return IdState.apply(g)

    def modify(self, f: Callable[[S], S]) -> 'IdState[S, None]':
        return IdState.apply(lambda s: monad.pure((f(s), None)))

    def modify_f(self, f: Callable[[S], Id[S]]) -> 'IdState[S, None]':
        return IdState.apply(lambda s: f(s).map(lambda a: (a, None)))

    def get(self) -> 'IdState[S, S]':
        return self.inspect(lambda a: a)

    @property
    def unit(self) -> 'IdState[S, None]':
        return IdState.pure(None)



class IdStateMeta(ImplicitsMeta):

    def cons(self, run_f: Id[Callable[[S], Id[Tuple[S, A]]]]) -> 'IdState[S, A]':
        return self(run_f)

    def apply(self, f: Callable[[S], Id[Tuple[S, A]]]) -> 'IdState[S, A]':
        return self.cons(monad.pure(f))

    def apply_f(self, run_f: Id[Callable[[S], Id[Tuple[S, A]]]]) -> 'IdState[S, A]':
        return self.cons(run_f)

    def inspect(self, f: Callable[[S], A]) -> 'IdState[S, A]':
        def g(s: S) -> Id[Tuple[S, A]]:
            return monad.pure((s, f(s)))
        return self.apply(g)

    def inspect_f(self, f: Callable[[S], Id[A]]) -> 'IdState[S, A]':
        def g(s: S) -> Id[Tuple[S, A]]:
            return f(s).map(lambda a: (s, a))
        return self.apply(g)

    def pure(self, a: A) -> 'IdState[S, A]':
        return self.apply(lambda s: monad.pure((s, a)))

    def reset(self, s: S, a: A) -> 'IdState[S, A]':
        return self.apply(lambda _: monad.pure((s, a)))

    def reset_t(self, t: Tuple[S, A]) -> 'IdState[S, A]':
        return self.apply(lambda _: monad.pure(t))

    def delay(self, fa: Callable[..., A], *a: Any, **kw: Any) -> 'IdState[S, A]':
        return self.apply(lambda s: monad.pure((s, fa(*a, **kw))))

    def lift(self, fa: Id[A]) -> 'IdState[S, A]':
        def g(s: S) -> Id[Tuple[S, A]]:
            return fa.map(lambda a: (s, a))
        return self.apply(g)

    def modify(self, f: Callable[[S], S]) -> 'IdState[S, None]':
        return self.apply(lambda s: monad.pure((f(s), None)))

    def modify_f(self, f: Callable[[S], Id[S]]) -> 'IdState[S, None]':
        return self.apply(lambda s: f(s).map(lambda a: (a, None)))

    def set(self, s: S) -> 'IdState[S, None]':
        return self.modify(lambda s0: s)

    def get(self) -> 'IdState[S, S]':
        return self.inspect(lambda a: a)

    @property
    def unit(self) -> 'IdState[S, None]':
        return IdState.pure(None)

    def s(self, tpe: Type[S]) -> IdStateCtor[S]:
        return IdStateCtor()



class IdState(Generic[S, A], StateT, ToStr, Implicits, implicits=True, auto=True, metaclass=IdStateMeta):

    def __init__(self, run_f: Id[Callable[[S], Id[Tuple[S, A]]]]) -> None:
        self.run_f = run_f

    @property
    def cls(self) -> Type['IdState[S, A]']:
        return type(self)

    def run(self, s: S) -> Id[Tuple[S, A]]:
        return self.run_f.flat_map(lambda f: f(s))

    def run_s(self, s: S) -> Id[S]:
        return self.run(s).map(lambda a: a[0])

    def run_a(self, s: S) -> Id[S]:
        return self.run(s).map(lambda a: a[1])

    def _arg_desc(self) -> List[str]:
        return List(str(self.run_f))

    def flat_map_f(self, f: Callable[[A], Id[B]]) -> 'IdState[S, B]':
        def h(s: S, a: A) -> Id[Tuple[S, B]]:
            return f(a).map(lambda b: (s, b))
        def g(fsa: Id[Tuple[S, A]]) -> Id[Tuple[S, B]]:
            return fsa.flat_map2(h)
        run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
        return self.cls.apply_f(run_f1)

    def transform(self, f: Callable[[Tuple[S, A]], Tuple[S, B]]) -> 'IdState[S, B]':
        def g(fsa: Id[Tuple[S, A]]) -> Id[Tuple[S, B]]:
            return fsa.map2(f)
        run_f1 = self.run_f.map(lambda sfsa: lambda a: g(sfsa(a)))
        return self.cls.apply_f(run_f1)

    def transform_s(self, f: Callable[[R], S], g: Callable[[R, S], R]) -> 'IdState[R, A]':
        def trans(sfsa: Callable[[S], Id[Tuple[S, A]]], r: R) -> Id[Tuple[R, A]]:
            s = f(r)
            return sfsa(s).map2(lambda s, a: (g(r, s), a))
        return self.cls.apply_f(self.run_f.map(curried(trans)))

    def transform_f(self, tpe: Type[ST1], f: Callable[[Id[Tuple[S, A]]], Any]) -> ST1:
        def trans(s: S) -> Any:
            return f(self.run(s))
        return tpe.apply(trans)  # type: ignore

    def zoom(self, l: UnboundLens) -> 'IdState[R, A]':
        return self.transform_s(l.get(), lambda r, s: l.set(s)(r))

    transform_s_lens = zoom

    def read_zoom(self, l: UnboundLens) -> 'IdState[R, A]':
        return self.transform_s(l.get(), lambda r, s: r)

    transform_s_lens_read = read_zoom

    def flat_map(self, f: Callable[[A], 'IdState[S, B]']) -> 'IdState[S, B]':
        return Monad_IdState.flat_map(self, f)


def run_function(s: IdState[S, A]) -> Id[Callable[[S], Id[Tuple[S, A]]]]:
    try:
        return s.run_f
    except Exception as e:
        if not isinstance(s, IdState):
            raise TypeError(f'flatMapped {s} into IdState')
        else:
            raise


class IdStateMonad(Monad, tpe=IdState):

    def pure(self, a: A) -> IdState[S, A]:  # type: ignore
        return IdState.pure(a)

    def flat_map(  # type: ignore
            self,
            fa: IdState[S, A],
            f: Callable[[A], IdState[S, B]]
    ) -> IdState[S, B]:
        def h(s: S, a: A) -> Id[Tuple[S, B]]:
            return f(a).run(s)
        def g(fsa: Id[Tuple[S, A]]) -> Id[Tuple[S, B]]:
            return fsa.flat_map2(h)
        def i(sfsa: Callable[[S], Id[Tuple[S, A]]]) -> Callable[[S], Id[Tuple[S, B]]]:
            return lambda a: g(sfsa(a))
        run_f1 = run_function(fa).map(i)
        return IdState.apply_f(run_f1)


Monad_IdState = IdStateMonad()


class IdStateZip(Zip, tpe=IdState):

    def zip(
            self,
            fa: IdState[S, A],
            fb: IdState[S, A],
            *fs: IdState[S, A],
    ) -> IdState[S, List[A]]:
        v = ListTraverse().sequence(List(fa, fb, *fs), IdState)  # type: ignore
        return cast(IdState[S, List[A]], v)



__all__ = ('IdState',)
