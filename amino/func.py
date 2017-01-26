from functools import wraps, partial, singledispatch
from inspect import getfullargspec
import typing
from typing import Callable, Union, Any, Dict

import fn

from amino.util.string import snake_case


class F(fn.F):

    def __truediv__(self, f):
        return self >> (lambda a: a / f)

    def __floordiv__(self, f):
        return self >> (lambda a: a // f)

    @property
    def name(self):
        from amino.anon import AnonCallable
        f = (
            self.f.func
            if isinstance(self.f.func, AnonCallable) else
            self.f.func.__name__
        ) if self._is_partial else self.f.__name__
        return str(f)

    @property
    def _is_partial(self):
        return isinstance(self.f, partial)

    def __str__(self):
        from amino.anon import format_funcall
        rep = (format_funcall(self.name, self.f.args, self.f.keywords)
               if self._is_partial
               else '{}()'.format(self.name))
        return 'F({})'.format(rep)


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

    def __call__(self, a):
        return a

    def __str__(self):
        return '(a => a)'

I = Identity()


class Val:

    def __init__(self, value) -> None:
        self.value = value

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


def dispatch(obj: Any, tpes: typing.List[type], prefix: str,
             default: Callable=None) -> Any:
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

__all__ = ('curried', 'F', 'I', 'flip', 'call_by_name', 'Val', 'ReplaceVal',
           'dispatch', 'dispatch_with', 'is_not_none')
