import abc
import re
from typing import Callable, Tuple

import tryp.func
from tryp.tc.apply import Apply
from tryp.tc.functor import F, A, B


class FlatMap(Apply):
    _flat_map_re = re.compile('^flat_map(\d+)$')

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

    def __getattr__(self, name):
        match = self._flat_map_re.match(name)
        if match is None:
            return super().__getattr__(name)
        else:
            return tryp.func.F(self.flat_map_n, int(match.group(1)))

    def flat_map_n(self, num, fa: F, f: Callable[..., F]) -> F:
        def wrapper(args):
            if len(args) != num:
                msg = 'passed {} args to {}.flat_map{}'
                name = self.__class__.__name__
                raise TypeError(msg.format(len(args), name, num))
            return f(*args)
        return self.flat_map(fa, wrapper)

__all__ = ('FlatMap',)
