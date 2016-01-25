import abc
from typing import Callable, Tuple

from tryp.tc.apply import Apply
from tryp.tc.functor import F, A, B


class FlatMap(Apply):

    def ap(self, fa: F, ff: F):
        return self.flat_map(ff, lambda f: self.map(fa, f))

    @abc.abstractmethod
    def flat_map(self, fa: F, f: Callable[[A], F]) -> F:
        ...

    def flat_smap(self, fa: F, f: Callable[..., F]) -> F:
        return self.flat_map(fa, lambda v: f(*v))

    def __floordiv__(self, fa, f):
        return self.flat_map(fa, f)

    def flat_map2(self, fa: F, fb: B, f: Callable[[A, B], F]) -> F:
        def unpack(tp: Tuple[A, B]):
            return f(tp[0], tp[1])
        return self.flat_map(self.product(fa, fb), unpack)  # type: ignore

    def product(self, fa: F, fb: F) -> F:
        return self.flat_map(fa, lambda a: self.map(fb, lambda b: (a, b)))

__all__ = ('FlatMap')
