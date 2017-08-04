from functools import wraps, partial, singledispatch
from inspect import getfullargspec
import typing
from typing import Callable, Union, Any, Dict, TypeVar, Tuple

from amino.util.string import snake_case

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


def dispatch(obj: Any, tpes: typing.List[type], prefix: str, default: Callable=None) -> Any:
    @singledispatch
    def main(o, *a, **kw):
        if default is None:
            msg = 'no dispatcher defined for {} on {} {}'
            raise TypeError(msg.format(o, obj.__class__.__name__, prefix))
        else:
            default(o, *a, **kw)
    for tpe in tpes:
        fun = getattr(obj, '{}{}'.format(prefix, snake_case(tpe.__name__)))
        main.register(tpe)(fun)
    return main


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


def is_not_none(a):
    return a is not None


def tupled2(f: Callable[[A, B], C]) -> Callable[[Tuple[A, B]], C]:
    def wrap(a: Tuple[A, B]) -> C:
        return f(a[0], a[1])
    return wrap

__all__ = ('curried', 'I', 'flip', 'call_by_name', 'Val', 'ReplaceVal', 'dispatch', 'dispatch_with', 'is_not_none',
           'tupled2')
