from typing import Callable, Tuple

from amino.anon.prod.attr import _
from amino.anon.prod.method import Anon, MethodRef, __, MethodChain, AnonChain


def make_complex(args: list) -> Tuple[tuple, tuple, int, int]:
    i_strict, i_lambda, i_param = 0, 0, 0
    ordered = ''
    stricts = ''
    lambdas = ''
    params = ''
    rest = []
    lambda_args = []
    for a in args:
        if a is _:
            i_param += 1
            arg = f'y{i_param},'
            ordered += arg
            params += arg
        elif isinstance(a, Anon):
            i_param += 1
            i_lambda += 1
            arg = f'y{i_param},'
            ordered += f'l{i_lambda}.__substitute_object__(y{i_param}),'
            params += arg
            lambdas += f'l{i_lambda},'
            lambda_args.append(a)
        else:
            i_strict += 1
            arg = f'x{i_strict},'
            ordered += arg
            stricts += arg
            rest.append(a)
    rep = f'lambda f: lambda {lambdas}: lambda {params}: lambda {stricts}: f({ordered})'
    return lambda_args, rest, rep, eval(rep), i_param


class ComplexLambda:

    def __init__(self, func: Callable, a: tuple, kw: dict) -> None:
        self.__func = func
        self.__args = a
        self.__kwargs = kw
        self.__qualname__ = self.__func.__name__
        self.__name__ = self.__func.__name__
        self.__annotations__ = {}
        self.__lambda_args, self.__rest, self.__repr, self.__lambda, self.__param_count = make_complex(self.__args)

    def __call__(self, *a, **kw):
        return self.__lambda(self.__func)(*self.__lambda_args)(*a)(*self.__rest)

    def __str__(self) -> str:
        return self.__repr

    def __rshift__(self, f):
        return AnonChain(self, f, self.__param_count)

    def __getattr__(self, name):
        return MethodChain(self, f'a.{name}')


class LazyMethod(Anon):

    def __init__(self, obj, attr: MethodRef) -> None:
        self.__obj = obj
        self.__attr = attr
        self.__name__ = self.__attr.__name__

    def __call__(self, *a, **kw):
        return self.__attr(*a, **kw)(self.__obj)

    def __getattr__(self, name: str):
        return LazyMethod(self.__obj, getattr(self.__attr, name))


class L:

    def __init__(self, func) -> None:
        self.__func = func

    def __call__(self, *a, **kw):
        return ComplexLambda(self.__func, a, kw)

    def __getattr__(self, name):
        return L(LazyMethod(self.__func, getattr(__, name)))

__all__ = ('L',)
