import abc
import re
from typing import TypeVar, Generic, Callable

import tryp.func
from tryp.tc.base import TypeClass

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Functor(Generic[F], TypeClass):
    _map_re = re.compile('^map(\d+)$')

    @abc.abstractmethod
    def map(self, fa: F, f: Callable[[A], B]) -> F:
        ...

    def __truediv__(self, fa, f):
        return self.map(fa, f)

    def smap(self, fa: F, f: Callable[..., B]) -> F:
        return self.map(fa, lambda v: f(*v))

    def ssmap(self, fa: F, f: Callable[..., B]) -> F:
        return self.map(fa, lambda v: f(**v))

    def __getattr__(self, name):
        match = self._map_re.match(name)
        if match is None:
            return super().__getattr__(name)
        else:
            return tryp.func.F(self.map_n, int(match.group(1)))

    def map_n(self, num, fa: F, f: Callable[..., B]) -> F:
        def wrapper(args):
            if len(args) != num:
                msg = 'passed {} args to {}.map{}'
                name = self.__class__.__name__
                raise TypeError(msg.format(len(args), name, num))
            return f(*args)
        return self.map(fa, wrapper)

    def pair(self, fa: F, f: Callable[[A], B]) -> F:
        return self.map(fa, lambda a: (a, f(a)))

    def flat_pair(self, fa: F, f: Callable[[A], 'tryp.maybe.Maybe[B]']) -> F:
        return self.flat_map(fa, lambda a: f(a).map(lambda b: (a, b)))

__all__ = ('Functor',)
