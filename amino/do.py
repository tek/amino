from typing import TypeVar, Callable, Any, Generator, cast
import functools

from amino.tc.base import Implicits

F = TypeVar('F', bound=Implicits)
A = TypeVar('A')


def do(f: Callable[..., Generator[F, A, F]]) -> Callable:
    @functools.wraps(f)
    def do_loop(*a: Any, **kw: Any) -> F:
        itr = f(*a, **kw)
        try:
            c = itr.send(cast(A, None))
            while True:
                cn = c.flat_map(itr.send)
                if cn is c:
                    return cn
                c = cn
        except StopIteration:
            return c
    return do_loop

__all__ = ('do',)
