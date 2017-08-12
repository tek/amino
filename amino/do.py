from typing import TypeVar, Callable, Any, Generator, cast, Optional
import functools

from amino.tc.base import Implicits

F = TypeVar('F', bound=Implicits)
A = TypeVar('A')


def do(f: Callable[..., Generator[F, A, F]]) -> Callable:
    @functools.wraps(f)
    def do_loop(*a: Any, **kw: Any) -> F:
        itr = f(*a, **kw)
        c: Optional[F] = None
        def send(val: A) -> F:
            nonlocal c
            try:
                c = itr.send(val)
                return c.flat_map(send)
            except StopIteration:
                return cast(F, c)
        return send(cast(A, None))
    return do_loop

__all__ = ('do',)
