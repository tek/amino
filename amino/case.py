from typing import Type, Generic, Any, TypeVar, GenericMeta
from functools import singledispatch, update_wrapper

from amino.util.string import snake_case
from amino import ADT

Alg = TypeVar('Alg')
A = TypeVar('A')
B = TypeVar('B')


def case_dispatch(cls: type, alg: Type[Alg]) -> dict:
    has_default = hasattr(cls, 'case_default')
    @singledispatch
    def case(self, o: A, *a: Any, **kw: Any) -> B:
        if has_default:
            return self.case_default(o, *a, **kw)
        else:
            raise TypeError(f'no case defined for {o} on {cls.__name__}')
    for tpe in alg.sub:
        fun = getattr(cls, snake_case(tpe.__name__), None)
        if fun is None and not has_default:
            raise TypeError(f'no case defined for {tpe} on {cls.__name__}')
        case.register(tpe)(fun)
    def wrapper(*args, **kw):
        return case.dispatch(args[1].__class__)(*args, **kw)
    wrapper.register = case.register
    wrapper.dispatch = case.dispatch
    wrapper.registry = case.registry
    wrapper._clear_cache = case._clear_cache
    update_wrapper(wrapper, case)
    return wrapper


class CaseMeta(GenericMeta):

    def __new__(cls, name: str, bases: tuple, namespace: dict, alg: Type[Alg]=None, **kw: Any) -> type:
        inst = super().__new__(cls, name, bases, namespace, **kw)
        if alg is not None:
            inst.case = case_dispatch(inst, alg)
        return inst


class Case(Generic[Alg, B], metaclass=CaseMeta):

    @classmethod
    def match(cls, *a, **kw) -> B:
        obj = cls()
        return obj.case(*a, **kw)

    def __call__(self, scrutinee: Alg, *a: Any, **kw: Any) -> B:
        return self.case(scrutinee, *a, **kw)


class CaseRecMeta(GenericMeta):

    def __new__(cls, name: str, bases: tuple, namespace: dict, alg: Type[Alg]=None, **kw: Any) -> type:
        inst = super().__new__(cls, name, bases, namespace, **kw)
        if alg is not None:
            inst.case = case_dispatch(inst, alg)
        return inst


class CaseRec(Generic[Alg, A], metaclass=CaseRecMeta):

    def __call__(self, scrutinee: Alg, *a: Any, **kw: Any) -> 'Rec[Alg, A]':
        return Rec(self, scrutinee, a, kw)


class RecStep(Generic[Alg, A], ADT['RecStep[Alg, A]']):
    pass


class Rec(Generic[Alg, A], RecStep[Alg, A]):

    def __init__(self, func: CaseRec[Alg, A], scrutinee: Alg, args: list, kwargs: dict) -> None:
        self.func = func
        self.scrutinee = scrutinee
        self.args = args
        self.kwargs = kwargs

    def eval(self) -> A:
        return eval_case_rec(self)


class Term(Generic[Alg, A], RecStep[Alg, A]):

    def __init__(self, result: A) -> None:
        self.result = result


def eval_case_rec(step: Rec[Alg, A]) -> A:
    while True:
        step = step.func.case(step.scrutinee, *step.args, **step.kwargs)
        if isinstance(step, Term):
            return step.result
        elif not isinstance(step, Rec):
            raise Exception(f'invalid result in CaseRec step: {step}')


__all__ = ('Case', 'CaseRec', 'Term')
