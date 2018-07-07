from typing import Iterable, Any, Type, TypeVar, _GenericAlias

from amino import do, Either, Do, Maybe, Right, Left, Lists

A = TypeVar('A')


def qualified_type(tpe: Type[A]) -> str:
    return tpe.__name__ if tpe.__module__ == 'builtins' else f'{tpe.__module__}.{tpe.__name__}'


def qualified_name(inst: Any) -> str:
    return inst.__name__ if inst.__module__ == 'builtins' else f'{inst.__module__}.{inst.__name__}'


@do(Either[str, type])
def type_arg(tpe: type, index: int) -> Do:
    def error() -> str:
        return f'{tpe} has no type args'
    raw = yield Maybe.getattr(tpe, '__args__').to_either_f(error)
    types = yield Right(Lists.wrap(raw)) if isinstance(raw, Iterable) else Left(error())
    yield types.lift(index).to_either_f(lambda: f'{tpe} has less than {index + 1} args')


def first_type_arg(tpe: type) -> Either[str, type]:
    return type_arg(tpe, 0)


def normalize_generic_type(tpe: type) -> type:
    return (
        tpe.__origin__
        if isinstance(tpe, _GenericAlias) else
        tpe
    )


def qualname(a: Any) -> str:
    return (
        a.__qualname__
        if hasattr(a, '__qualname__') else
        a.__origin__.__qualname__
        if hasattr(a, '__origin__') else
        a.__qualname__
    )


def is_subclass(tpe: Any, base: type) -> bool:
    def error():
        raise TypeError(f'argument `{tpe}` to `is_subclass({base})` is neither TypeVar nor type')
    return (
        False
        if isinstance(tpe, TypeVar) else
        issubclass(normalize_generic_type(tpe), base)
        if isinstance(tpe, (type, _GenericAlias)) else
        error()
    )


__all__ = ('qualified_type', 'type_arg', 'first_type_arg', 'qualified_name', 'qualname', 'normalize_generic_type',
           'is_subclass',)
