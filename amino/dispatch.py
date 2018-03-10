from functools import singledispatch, update_wrapper
import typing
from typing import Callable, Any, Dict, TypeVar, Type, Generic, GenericMeta

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
    return dispatch(obj, alg.sub, prefix, default)


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


def patmat_dispatch(cls: type, alg: Type[Alg]) -> dict:
    has_default = hasattr(cls, 'patmat_default')
    @singledispatch
    def patmat(self, o: A, *a: Any, **kw: Any) -> B:
        if has_default:
            return self.patmat_default(o, *a, **kw)
        else:
            raise TypeError(f'no case defined for {o} on {cls.__name__}')
    for tpe in alg.sub:
        fun = getattr(cls, snake_case(tpe.__name__), None)
        if fun is None and not has_default:
            raise TypeError(f'no case defined for {tpe} on {cls.__name__}')
        patmat.register(tpe)(fun)
    def wrapper(*args, **kw):
        return patmat.dispatch(args[1].__class__)(*args, **kw)
    wrapper.register = patmat.register
    wrapper.dispatch = patmat.dispatch
    wrapper.registry = patmat.registry
    wrapper._clear_cache = patmat._clear_cache
    update_wrapper(wrapper, patmat)
    return wrapper


class PatMatMeta(GenericMeta):

    def __new__(cls, name: str, bases: tuple, namespace: dict, alg: Type[Alg]=None, **kw: Any) -> type:
        inst = super().__new__(cls, name, bases, namespace, **kw)
        if alg is not None:
            inst.patmat = patmat_dispatch(inst, alg)
        return inst


class PatMat(Generic[Alg, B], metaclass=PatMatMeta):

    @classmethod
    def match(cls, *a, **kw) -> B:
        obj = cls()
        return obj.patmat(*a, **kw)

    def __call__(self, scrutinee: Alg, *a: Any, **kw: Any) -> B:
        return self.patmat(scrutinee, *a, **kw)


__all__ = ('dispatch', 'dispatch_alg', 'dispatch_with')
