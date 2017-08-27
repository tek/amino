from types import GeneratorType
from typing import TypeVar, Callable, Any, Generator, cast, Optional
import functools

from amino.tc.base import Implicits
from amino.tc.monad import Monad

F = TypeVar('F', bound=Implicits)
A = TypeVar('A')


def do(f: Callable[..., Generator[F, A, F]]) -> Callable:
    @functools.wraps(f)
    def do_loop(*a: Any, **kw: Any) -> F:
        itr = f(*a, **kw)
        if not isinstance(itr, GeneratorType):
            raise Exception(f'function `{f.__qualname__}` decorated with `do` does not produce a generator')
        c: Optional[F] = None
        m: Optional[Monad[F]] = None
        def send(val: A) -> F:
            nonlocal c, m
            try:
                c = itr.send(val)
                m = Monad.fatal_for(c)
                return c.flat_map(send)
            except StopIteration:
                return m.pure(val)
        return send(cast(A, None))
    return do_loop

__all__ = ('do',)
