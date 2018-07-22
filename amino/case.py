from types import SimpleNamespace
from typing import Type, Generic, Any, TypeVar, Callable, Tuple, _GenericAlias, get_type_hints
import inspect

from amino.util.string import snake_case
from amino import ADT, Map, List, Lists, do, Do, Either, Try, Just, Nothing, Maybe
from amino.algebra import Algebra
from amino.logging import module_log

log = module_log()
Alg = TypeVar('Alg', bound=Algebra)
C = TypeVar('C', bound=Alg)
A = TypeVar('A')
B = TypeVar('B')


class CaseMeta(type):

    def __new__(cls: type, name: str, bases: tuple, namespace: SimpleNamespace, alg: Type[Alg]=None, **kw: Any) -> type:
        inst = super().__new__(cls, name, bases, namespace, **kw)
        if alg is not None:
            inst.case = case_dispatch(inst, alg)
        return inst


class Case(Generic[Alg, B], metaclass=CaseMeta):

    @classmethod
    def match(cls, scrutinee: Alg, *a: Any, **kw: Any) -> B:
        return cls().case(scrutinee, *a, **kw)

    def __call__(self, scrutinee: Alg, *a: Any, **kw: Any) -> B:
        return self.case(scrutinee, *a, **kw)


def normalize_type(tpe: Type[C]) -> Type[C]:
    return getattr(tpe, '__origin__', tpe)


def case_list(
        cls: Type[Case[C, B]],
        variants: List[Type[C]],
        alg: Type[C],
        has_default: bool,
) -> Map[Type[C], Callable[[Case[C, B]], B]]:
    @do(Maybe[Tuple[Type[C], Callable[[Case[C, B]], B]]])
    def is_handler(name: str, f: Callable) -> Do:
        effective = getattr(f, '__do_original', f)
        hints = yield Try(get_type_hints, effective).to_maybe
        spec = yield Try(inspect.getfullargspec, effective).to_maybe
        param_name = yield Lists.wrap(spec.args).lift(1)
        param_type = yield Map(hints).lift(param_name)
        yield (
            Just((normalize_type(param_type), f))
            if isinstance(param_type, type) and issubclass(param_type, alg) else
            Just((normalize_type(param_type), f))
            if isinstance(param_type, _GenericAlias) and issubclass(param_type.__origin__, alg) else
            Nothing
        )
    handlers = Lists.wrap(inspect.getmembers(cls, inspect.isfunction)).flat_map2(is_handler)
    def find_handler(variant: Type[C]) -> Callable[[Case[C, B]], B]:
        def not_found() -> None:
            if not has_default:
                raise Exception(f'no case defined for {variant} on {cls.__name__}')
        def match_handler(tpe: type, f: Callable) -> Maybe[Callable[[Case[C, B]], B]]:
            return Just(f) if issubclass(tpe, variant) else Nothing
        return handlers.find_map2(match_handler).get_or_else(not_found)
    return variants.map(find_handler)


# TODO determine default case from param type being the ADT
def case_dispatch(cls: Type[Case[C, B]], alg: Type[C]) -> Callable[[Case[C, B], C], B]:
    def error(func: Case[C, B], variant: Alg, *a: Any, **kw: Any) -> None:
        raise TypeError(f'no case defined for {variant} on {cls.__name__}')
    default = getattr(cls, 'case_default', error)
    has_default = default is not error
    cases = case_list(cls, alg.__algebra_variants__.sort_by(lambda a: a.__algebra_index__), alg, has_default)
    length = cases.length
    def case(func: Case[C, B], scrutinee: C, *a: Any, **kw: Any) -> B:
        index = getattr(scrutinee, '__algebra_index__', None)
        handler = (cases[index] or default) if index is not None and index < length else default
        return handler(func, scrutinee, *a, **kw)
    return case


class CaseRecMeta(type):

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
