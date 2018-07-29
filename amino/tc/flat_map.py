import abc
from typing import Callable, Iterable, TypeVar, Generic, List

import amino  # NOQA
from amino.tc.apply import Apply
from amino.func import I
from amino.tc.base import tc_prop
from amino.tc.apply_n import ApplyN

F = TypeVar('F')
G = TypeVar('G')
A = TypeVar('A')
B = TypeVar('B')


class FlatMap(Apply, ApplyN):

    def apply_n_funcs(self) -> List[str]:
        return super().apply_n_funcs() + ['flat_map', 'product']

    def ap(self, fa: F, ff: F):
        f = lambda f: self.map(fa, f)
        return self.flat_map(ff, f)

    @abc.abstractmethod
    def flat_map(self, fa: F, f: Callable[[A], G]) -> G:
        ...

    def __floordiv__(self, fa, f):
        return self.flat_map(fa, f)

    def product(self, fa: F, fb: F) -> F:
        f = lambda a: self.map(fb, lambda b: (a, b))
        return self.flat_map(fa, f)

    __and__ = product

    def product_n(self, num: int, fa: F, *fs: Iterable[F]):
        from amino.list import List
        if len(fs) != num:
            msg = 'passed {} args to {}.product{}'
            name = self.__class__.__name__
            raise TypeError(msg.format(len(fs), name, num))
        def add(a, b):
            return self.flat_map(a, lambda a: self.map(b, lambda b: a + (b,)))
        init = self.map(fa, lambda a: (a,))
        return List.wrap(fs).fold_left(init)(add)

    def flat_pair(self, fa: F, f: Callable[[A], 'amino.maybe.Maybe[B]']) -> F:
        cb = lambda a: f(a).map(lambda b: (a, b))
        return self.flat_map(fa, cb)

    def flat_replace(self, fa: F, fb: F) -> F:
        cb = lambda a: fb
        return self.flat_map(fa, cb)

    def and_then(self, fa: F, fb: F) -> F:
        cb = lambda a: fb
        return self.flat_map(fa, cb)

    @tc_prop
    def join(self, fa: F) -> F:
        return self.flat_map(fa, I)

__all__ = ('FlatMap',)
