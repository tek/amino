import abc
from typing import Type, Generic, Any, TypeVar, GenericMeta
from functools import singledispatch, update_wrapper

from amino.util.string import snake_case
from amino import Dat, ADT

Alg = TypeVar('Alg')
A = TypeVar('A')
B = TypeVar('B')


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


class PatMatRecMeta(GenericMeta):

    def __new__(cls, name: str, bases: tuple, namespace: dict, alg: Type[Alg]=None, **kw: Any) -> type:
        inst = super().__new__(cls, name, bases, namespace, **kw)
        if alg is not None:
            inst.patmat = patmat_dispatch(inst, alg)
        return inst


class PatMatRec(Generic[Alg, A], metaclass=PatMatRecMeta):

    def __call__(self, scrutinee: Alg, *a: Any, **kw: Any) -> 'Rec[Alg, A]':
        return Rec(self, scrutinee, a, kw)


class Step(Generic[A], ADT['Step[A]']):
    pass


class Rec(Generic[Alg, A], Step[A]):

    def __init__(self, func: PatMatRec[Alg, A], scrutinee: Alg, args: list, kwargs: dict) -> None:
        self.func = func
        self.scrutinee = scrutinee
        self.args = args
        self.kwargs = kwargs

    def eval(self) -> A:
        return eval_pat_mat_rec(self)


class Term(Generic[A], Step[A]):

    def __init__(self, result: A) -> None:
        self.result = result


def eval_pat_mat_rec(step: Rec) -> None:
    while True:
        step = step.func.patmat(step.scrutinee, *step.args, **step.kwargs)
        if isinstance(step, Term):
            return step.result
        elif not isinstance(step, Rec):
            raise Exception(f'invalid result in PatMatRec step: {step}')


__all__ = ('PatMat', 'PatMatRec', 'Term')
