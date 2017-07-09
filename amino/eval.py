import abc
from typing import Generic, TypeVar, Callable, Tuple, Any, Union

from fn.recur import tco

from amino.lazy import lazy
from amino.tc.base import Implicits
from amino.tc.monad import Monad
from amino import List

A = TypeVar('A')
B = TypeVar('B')


class Eval(Generic[A], Implicits, implicits=True, auto=True):

    @abc.abstractmethod
    def _value(self) -> A:
        ...

    @property
    def value(self) -> A:
        return self._value()

    @abc.abstractproperty
    def memoize(self) -> 'Eval[A]':
        ...


class Now(Generic[A], Eval[A]):

    def __init__(self, value: A) -> None:
        self.strict = value

    def _value(self) -> A:
        return self.strict

    @property
    def memoize(self) -> Eval[A]:
        return self


class Later(Generic[A], Eval[A]):

    def __init__(self, f: Callable[[], A]) -> None:
        self.f = f

    @lazy
    def _memoized(self) -> A:
        return self.f()

    def _value(self) -> A:
        return self._memoized

    @property
    def memoize(self) -> Eval[A]:
        return self


class Always(Generic[A], Eval[A]):

    def __init__(self, f: Callable[[], A]) -> None:
        self.f = f

    def _value(self) -> A:
        return self.f()

    @property
    def memoize(self) -> Eval[A]:
        return Later(self.f)


class Call(Generic[A], Eval[A]):

    def __init__(self, thunk: Callable[[], Eval[A]]) -> None:
        self.thunk = thunk

    @staticmethod
    def _loop(ev: Eval[A]) -> Eval[A]:
        def loop1(s: Eval[A]) -> Eval[A]:
            return loop(s.run)
        @tco
        def loop(e: Eval[A]) -> Tuple[bool, Tuple[Eval[A]]]:
            if isinstance(e, Call):
                return True, (e.thunk(),)
            elif isinstance(e, Compute):
                return False, (Compute(e.start, loop1),)
            else:
                return False, e
        return loop(ev)


class Compute(Generic[A, B], Eval[A]):

    def __init__(self, start: Callable[[], Eval[B]], run: Callable[[B], Eval[A]]) -> None:
        self.start = start
        self.run = run

    def _value(self) -> A:
        C = Callable[[Any], Eval[Any]]
        R = Tuple[bool, Union[Tuple[Eval[Any], List[C]], Any]]
        def loop_compute(c: Compute[Any, Any], fs: List[C]) -> R:
            cc = c.start()
            return (
                (True, (cc.start(), fs.cons(c.run).cons(cc.run)))
                if isinstance(cc, Compute) else
                (True, (c.run(cc._value()), fs))
            )
        def loop_other(e: Eval[Any], fs: List[C]) -> R:
            return fs.detach_head.map2(lambda fh, ft: (True, (fh(e._value()), ft))) | (False, e._value())
        @tco
        def loop(e: Eval[Any], fs: List[C]) -> R:
            return (
                loop_compute(e, fs)
                if isinstance(e, Compute) else
                loop_other(e, fs)
            )
        return loop(self, List())

    @property
    def memoize(self) -> Eval[A]:
        return Later(self)


class EvalMonad(Monad, tpe=Eval):

    def pure(self, a: A) -> Eval[A]:
        return Now(a)

    def flat_map(self, fa: Eval[A], f: Callable[[A], Eval[B]]) -> Eval[B]:
        def f1(s: A) -> Eval[B]:
            return Compute(lambda: fa.run(s), f)
        start, run = (
            (fa.start, f1)
            if isinstance(fa, Compute) else
            (fa.thunk, f)
            if isinstance(fa, Call) else
            (lambda: fa, f)
        )
        return Compute(start, run)

__all__ = ('Eval',)
