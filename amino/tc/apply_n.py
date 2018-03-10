import re
import abc
from typing import Callable, Any, List, TypeVar

from amino.tc.base import TypeClass

A = TypeVar('A')
B = TypeVar('B')
F = TypeVar('F')


def apply_n(self: TypeClass, num: int, fa: F, f: Callable[..., A], g: Callable[..., B], *a: Any) -> B:
    def wrapper(args: tuple):
        if len(args) != num:
            name = self.__class__.__name__
            msg = f'passed {len(args)} args to {name}.{g.__name__}{num}'
            raise TypeError(msg)
        return f(*args)
    return g(fa, wrapper, *a)


apply_n_rex = re.compile('^(.*)(\d+)$')


class ApplyN:

    @abc.abstractclassmethod
    def apply_n_funcs(self) -> List[str]:
        ...

    def __getattr__(self, name: str) -> Callable:
        def error() -> None:
            raise AttributeError(f'''`{self.__class__.__name__}` object has no attribute `{name}`''')
        match = apply_n_rex.match(name)
        if match is None:
            error()
        func = match.group(1)
        num = int(match.group(2))
        n_name = f'{func}_n'
        if hasattr(self, n_name):
            return lambda fa, f, *a: getattr(self, n_name)(num, fa, f, *a)
        if func not in self.apply_n_funcs():
            error()
        return lambda fa, f, *a: apply_n(self, num, fa, f, getattr(self, func), *a)


__all__ = ('apply_n', 'ApplyN')
