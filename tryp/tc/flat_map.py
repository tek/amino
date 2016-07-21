import abc
import re
from typing import Callable, Tuple, Iterable

import tryp.func
from tryp.tc.apply import Apply
from tryp.tc.functor import F, A, B


class FlatMap(Apply):
    _flat_map_re = re.compile('^flat_map(\d+)$')
    _product_re = re.compile('^product(\d+)$')

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
        flat_map = self._flat_map_re.match(name)
        product = self._product_re.match(name)
        if flat_map is not None:
            return tryp.func.F(self.flat_map_n, int(flat_map.group(1)))
        elif product is not None:
            return tryp.func.F(self.product_n, int(product.group(1)))
        else:
            return super().__getattr__(name)

    def flat_map_n(self, num, fa: F, f: Callable[..., F]) -> F:
        def wrapper(args):
            if len(args) != num:
                msg = 'passed {} args to {}.flat_map{}'
                name = self.__class__.__name__
                raise TypeError(msg.format(len(args), name, num))
            return f(*args)
        return self.flat_map(fa, wrapper)

    def product_n(self, num: int, fa: F, *fs: Iterable[F]):
        from tryp.list import List
        if len(fs) != num:
            msg = 'passed {} args to {}.product{}'
            name = self.__class__.__name__
            raise TypeError(msg.format(len(fs), name, num))
        def add(a, b):
            return self.flat_map(a, lambda a: self.map(b, lambda b: a + (b,)))
        init = self.map(fa, lambda a: (a,))
        return List.wrap(fs).fold_left(init)(add)

__all__ = ('FlatMap',)
