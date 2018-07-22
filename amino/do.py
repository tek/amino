from types import GeneratorType
from typing import TypeVar, Callable, Any, Generator, Type
import functools

from amino.tc.base import F
from amino.tc.monad import Monad

A = TypeVar('A')
B = TypeVar('B')
G = TypeVar('G', bound=F)
Do = Generator


# NOTE ostensibly, this cannot be tailrecced without separating strictly evaluated monadic composition from lazy ones.
# itr.gi_frame.f_lasti is the instruction pointer and could be used to detect laziness.
# NOTE due to the nature of generators, a do with a lazily evaluated monad cannot be executed twice.
# NOTE Lists don't work properly because the generator will be consumed by the first element
def do_impl(tpe: type, f: Callable[..., Generator[G, B, None]]) -> Callable[..., G]:
    @functools.wraps(f)
    def do_loop(*a: Any, **kw: Any) -> F[B]:
        m = Monad.fatal(tpe)
        itr = f(*a, **kw)
        if not isinstance(itr, GeneratorType):
            raise Exception(f'function `{f.__qualname__}` decorated with `do` does not produce a generator')
        @functools.wraps(f)
        def loop(val: B) -> F[B]:
            try:
                return m.flat_map(itr.send(val), loop)
            except StopIteration as e:
                return m.pure(val if e.value is None else e.value)
        return m.flat_map(m.pure(None), loop)
    return do_loop


def do(tpe: Type[A]) -> Callable[[Callable[..., Generator]], Callable[..., A]]:
    def deco(f: Callable[..., Generator]) -> Callable[..., A]:
        f.tpe = tpe
        f.__do = None
        f.__do_original = f
        return functools.wraps(f)(do_impl)(tpe, f)
    return deco

tdo = do

__all__ = ('do', 'F', 'tdo', 'Do')
