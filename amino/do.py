from types import GeneratorType
from typing import TypeVar, Callable, Any, Generator, cast, Type
import functools

from amino.tc.base import F
from amino.tc.monad import Monad

A = TypeVar('A')
B = TypeVar('B')
G = TypeVar('G', bound=F)
Do = Generator


# NOTE ostensibly, this cannot be tailrecced without separating strictly evaluated monadic composition from lazy ones.
# itr.gi_frame.f_lasti is the instruction pointer and could be used to detect laziness.
def untyped_do(f: Callable[..., Generator[G, B, None]]) -> Callable[..., G]:
    @functools.wraps(f)
    def do_loop(*a: Any, **kw: Any) -> F[B]:
        itr = f(*a, **kw)
        if not isinstance(itr, GeneratorType):
            raise Exception(f'function `{f.__qualname__}` decorated with `do` does not produce a generator')
        init = itr.send(None)
        m = Monad.fatal_for(init)
        @functools.wraps(f)
        def loop(val: B) -> F[B]:
            try:
                return m.flat_map(itr.send(val), loop)
            except StopIteration:
                return m.pure(val)
        return m.flat_map(init, loop)
    return do_loop


def do(tpe: Type[A]) -> Callable[[Callable[..., Generator]], Callable[..., A]]:
    def deco(f: Callable[..., Generator]) -> Callable[..., A]:
        return cast(Callable[[Callable[..., Generator]], Callable[..., A]], functools.wraps(f)(untyped_do))(f)
    return deco

tdo = do

__all__ = ('do', 'F', 'tdo', 'untyped_do', 'Do')
