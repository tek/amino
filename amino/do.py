from types import GeneratorType
from typing import TypeVar, Callable, Any, Generator, cast, Type
import functools

from amino.tc.base import F
from amino.tc.monad import Monad

A = TypeVar('A')
B = TypeVar('B')
G = TypeVar('G', bound=F)
Do = Generator


def untyped_do(f: Callable[..., Generator[G, B, None]]) -> Callable[..., G]:
    @functools.wraps(f)
    def do_loop(*a: Any, **kw: Any) -> F[B]:
        itr = f(*a, **kw)
        if not isinstance(itr, GeneratorType):
            raise Exception(f'function `{f.__qualname__}` decorated with `do` does not produce a generator')
        init = itr.send(None)
        m = Monad.fatal_for(init)
        def send(val: B) -> F[B]:
            try:
                return itr.send(val).flat_map(send)
            except StopIteration:
                nonlocal m
                return m.pure(val)
        return init.flat_map(send)
    return do_loop


def do(tpe: Type[A]) -> Callable[[Callable[..., Generator]], Callable[..., A]]:
    def deco(f: Callable[..., Generator]) -> Callable[..., A]:
        return cast(Callable[[Callable[..., Generator]], Callable[..., A]], untyped_do)(f)
    return deco

tdo = do

__all__ = ('do', 'F', 'tdo', 'untyped_do', 'Do')
