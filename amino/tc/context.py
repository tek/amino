import inspect
from typing import TypeVar, Callable, Any, Generic, Type
from functools import reduce

from amino import Map, Boolean
from amino.case import Case
from amino.algebra import Algebra

A = TypeVar('A')
B = TypeVar('B')
X = TypeVar('X')
Alg = TypeVar('Alg', bound=Algebra)


class Bindings:

    def __init__(self, bindings: Map[str, type]) -> None:
        self.bindings = bindings


def function_bindings_relay(f: Callable) -> Boolean:
    target = f.__do_original if hasattr(f, '__do') else f
    anno = inspect.getfullargspec(target).annotations
    return Boolean(anno.get('bindings', None) is Bindings)


def case_bindings_relay(pm: Type[Case[Alg, B]]) -> Boolean:
    return function_bindings_relay(pm.__init__)


def check_bound(rep: str, t: Type[A], b: Type[B], bindings: Map) -> None:
    binding = bindings.lift(t).get_or_fail(lambda: f'no binding for {t} => {b} in {rep}')
    b.m(binding).get_or_fail(lambda: f'no instance of {t} => {b} for {binding} in {rep}')


def check_bounds(rep: str, bounds: Map, bindings: Map) -> None:
    for t, b in bounds.items():
        check_bound(rep, t, b, bindings)


class BoundedFunction(Generic[A]):

    def __init__(self, f: Callable, bindings: Bindings, relay: Boolean) -> None:
        self.f = f
        self.bindings = bindings
        self.relay = relay

    def __call__(self, *a, **kw) -> Callable:
        return self.f(self.bindings, *a, **kw) if self.relay else self.f(*a, **kw)


class ContextBound(Generic[A]):

    def __init__(self, f: Callable, bounds: Map) -> None:
        self.f = f
        self.bounds = bounds
        self.relay = function_bindings_relay(f)

    def __call__(self, *a: Bindings, **kw) -> Callable:
        bindings = reduce(lambda a, b: a ** b.bindings, a, Map(kw))
        check_bounds(str(self.f), self.bounds, bindings)
        return BoundedFunction(self.f, Bindings(bindings), self.relay)

    def call(self, *a, **kw) -> A:
        return self.f(*a, **kw)


class BoundedCase(Generic[Alg, B]):

    def __init__(self, pm: Case[Alg, B], bindings: Bindings, relay: Boolean) -> None:
        self.pm = pm
        self.bindings = bindings
        self.relay = relay

    def __call__(self, *a, **kw) -> Callable:
        return self.pm(self.bindings, *a, **kw) if self.relay else self.pm(*a, **kw)


class CaseContextBound(Generic[Alg, B]):

    def __init__(self, pm: Type[Case[Alg, B]], bounds: Map) -> None:
        self.pm = pm
        self.bounds = bounds
        self.relay = case_bindings_relay(pm)

    def __call__(self, *a: Bindings, **kw: type) -> Case[Alg, B]:
        bindings = reduce(lambda a, b: a ** b.bindings, a, Map(kw))
        check_bounds(self.pm.__name__, self.bounds, bindings)
        return BoundedCase(self.pm, Bindings(bindings), self.relay)

    def call(self, *a, **kw) -> A:
        return self.pm(*a, **kw)


def context(*bindings: ContextBound, **tpes: Any) -> Callable:
    def dec(f: Callable) -> Callable:
        return (
            CaseContextBound(f, Map(tpes))
            if isinstance(f, type) and issubclass(f, Case) else
            ContextBound(f, Map(tpes))
        )
    return dec

__all__ = ('context',)
