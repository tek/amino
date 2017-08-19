from functools import wraps, partial
from inspect import getfullargspec
from typing import Callable, Union, Any, TypeVar, Tuple

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


def curried(func):
    @wraps(func)
    def _curried(*args, **kwargs):
        f = func
        count = 0
        while isinstance(f, partial):
            if f.args:
                count += len(f.args)
            f = f.func
        spec = getfullargspec(f)
        if count == len(spec.args) - len(args):
            return func(*args, **kwargs)
        else:
            return curried(partial(func, *args, **kwargs))
    return _curried


class Identity:

    def __init__(self) -> None:
        self.__name__ = 'identity'

    def __call__(self, a):
        return a

    def __str__(self):
        return '(a => a)'

I = Identity()


class Val:

    def __init__(self, value) -> None:
        self.value = value
        self.__name__ = self.__class__.__name__

    def __call__(self):
        return self.value

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)


class ReplaceVal(Val):

    def __call__(self, *a, **kw):
        return super().__call__()


def flip(a, b):
    return b, a

CallByName = Union[Any, Callable[[], Any]]


def call_by_name(b: CallByName):
    return b() if callable(b) else b


def is_not_none(a):
    return a is not None


def tupled2(f: Callable[[A, B], C]) -> Callable[[Tuple[A, B]], C]:
    def wrap(a: Tuple[A, B]) -> C:
        return f(a[0], a[1])
    return wrap

__all__ = ('curried', 'I', 'flip', 'call_by_name', 'Val', 'ReplaceVal', 'is_not_none', 'tupled2')
