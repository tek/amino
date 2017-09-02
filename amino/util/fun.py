from types import FunctionType, MethodType
from typing import Callable


def lambda_str(f: Callable) -> str:
    if isinstance(f, MethodType):
        return '{}.{}'.format(f.__self__.__class__.__name__, f.__name__)
    elif isinstance(f, FunctionType):
        return f.__name__
    elif isinstance(f, str):
        return f
    else:
        return str(f)


def format_funcall(fun: Callable, args: tuple, kwargs: dict) -> str:
    from amino.map import Map
    kw = Map(kwargs).map2('{}={!r}'.format)
    a = list(map(repr, args)) + list(kw)
    args_fmt = ', '.join(a)
    return '{}({})'.format(lambda_str(fun), args_fmt)

__all__ = ('lambda_str', 'format_funcall')
