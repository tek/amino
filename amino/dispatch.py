from functools import singledispatch
import typing
from typing import Callable, Any, Dict, TypeVar, Type

from amino.util.string import snake_case
from amino.algebra import Algebra

A = TypeVar('A')
B = TypeVar('B')
R = TypeVar('R')
Alg = TypeVar('Alg', bound=Algebra)


def dispatch(obj: B, tpes: typing.List[A], prefix: str, default: Callable[[A], R]=None) -> Callable[[A], R]:
    def error(o: A) -> None:
        msg = 'no dispatcher defined for {} on {} {}'
        raise TypeError(msg.format(o, obj.__class__.__name__, prefix))
    @singledispatch
    def main(o: A, *a: Any, **kw: Any) -> R:
        if default is None:
            error(o)
        else:
            return default(o, *a, **kw)
    for tpe in tpes:
        fun = getattr(obj, '{}{}'.format(prefix, snake_case(tpe.__name__)), None)
        if fun is None:
            error(tpe)
        main.register(tpe)(fun)
    return main


def dispatch_alg(obj: B, alg: Type[Alg], prefix: str='', default: Callable[[Alg], R]=None) -> Callable[[Alg], R]:
    return dispatch(obj, alg.__algebra_variants__, prefix, default)


def dispatch_with(rules: Dict[type, Callable], default: Callable=None):
    @singledispatch
    def main(o, *a, **kw):
        if default is None:
            msg = 'no dispatcher defined for {} {} ({})'
            raise TypeError(msg.format(type(o), o, rules))
        else:
            default(o, *a, **kw)
    for tpe, fun in rules.items():
        main.register(tpe)(fun)
    return main


__all__ = ('dispatch', 'dispatch_alg', 'dispatch_with')
