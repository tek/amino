from typing import Type, TypeVar

A = TypeVar('A')


def qualified_type(tpe: Type[A]) -> str:
    return tpe.__name__ if tpe.__module__ == 'builtins' else f'{tpe.__module__}.{tpe.__name__}'

__all__ = ('qualified_type',)
