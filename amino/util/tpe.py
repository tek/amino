from typing import Iterable

from typing import Type, TypeVar

from amino import do, Either, Do, Maybe, Right, Left, Lists

A = TypeVar('A')


def qualified_type(tpe: Type[A]) -> str:
    return tpe.__name__ if tpe.__module__ == 'builtins' else f'{tpe.__module__}.{tpe.__name__}'


@do(Either[str, type])
def type_arg(tpe: type, index: int) -> Do:
    def error() -> str:
        return f'{tpe} has no type args'
    raw = yield Maybe.getattr(tpe, '__args__').to_either_f(error)
    types = yield Right(Lists.wrap(raw)) if isinstance(raw, Iterable) else Left(error())
    yield types.lift(index).to_either_f(lambda: f'{tpe} has less than {index + 1} args')


def first_type_arg(tpe: type) -> Either[str, type]:
    return type_arg(tpe, 0)


__all__ = ('qualified_type', 'type_arg', 'first_type_arg')
