from typing import Any, Callable

from amino.anon.prod.method import Opers, Anon, AnonMethodCall


class AttrLambda(Opers, Anon):

    def __init__(self, pre: str) -> None:
        self.__pre = pre

    def __pre__(self) -> str:
        return self.__pre

    def __getattr__(self, name):
        return AttrLambda(f'{self.__pre}.{name}')

    def __getitem__(self, key):
        return AttrLambda(f'{self.__pre}[{key}]')

    def __repr__(self):
        return f'lambda a: {self.__pre}'

    def __call__(self, a: Any) -> Any:
        return self.__eval__()(a)

    def __substitute_object__(self, obj: Any) -> Callable:
        return self.__call__(obj)

    def __lop__(self, op, s, a):
        return AnonMethodCall(f'(lambda b: {self.__pre__()} {s} b)', (a,), {})

    def __rop__(self, op, s, a):
        return AnonMethodCall(f'(lambda b: b {s} {self.__pre__()})', (a,), {})

_ = AttrLambda('a')

__all__ = ('_',)
