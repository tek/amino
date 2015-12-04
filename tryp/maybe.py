from typing import TypeVar, Generic, Callable, Union, Tuple, Iterable
from functools import wraps, partial  # type: ignore
from operator import eq, is_not  # type: ignore

from fn import F, _  # type: ignore
from fn.op import identity  # type: ignore

A = TypeVar('A')

B = TypeVar('B')


class Maybe(Iterable[A], Generic[A]):

    def __new__(tp, value: A, checker=partial(is_not, None)):
        return Maybe.inst(value, checker)

    @staticmethod
    def inst(value: A, checker=partial(is_not, None)):
        return Just(value) if checker(value) else Empty()

    @staticmethod
    def from_call(callback: Callable[..., A], *args, **kwargs):
        '''Execute callback and catch possible (all by default)
        exceptions. If exception is raised Empty will be returned.
        '''
        exc = kwargs.pop('exc', Exception)
        try:
            return Maybe.inst(callback(*args, **kwargs))
        except exc:
            return Empty()

    @property
    def _get(self) -> Union[A, None]:
        pass

    def cata(self, f: Callable[[A], B], b: B) -> B:
        if self.isJust:
            return f(self._get)
        else:
            return b

    def map(self, f: Callable[[A], B]) -> 'Maybe[B]':
        return self.cata(F(lambda v: Just(v)) << F(f), Empty())

    def smap(self, f: Callable[[A], B]) -> 'Maybe[B]':
        return self.cata(F(lambda v: Just(v)) << F(lambda v: f(*v)), Empty())

    def flatMap(self, f: Callable[[A], 'Maybe[B]']) -> 'Maybe[B]':
        e = Empty()  # type: Maybe[B]
        return self.cata(f, e)

    def filter(self, f: Callable[[A], B]):
        l = lambda a: self if f(a) else Empty()
        return self.flatMap(l)

    def get_or_else(self, a: A):
        return self.cata(identity, a)

    def or_else(self, ma):
        return self.cata(lambda v: self, ma)

    def contains(self, v):
        return self.cata(_ == v, False)

    def zip(self, other: 'Maybe[B]') -> 'Maybe[Tuple[A, B]]':
        if self.isJust and other.isJust:
            return Just((self._get, other._get))
        else:
            return Empty()

    def __iter__(self):
        return iter(self.toList)

    @property
    def isJust(self):
        return (isinstance(self, Just))

    @property
    def toList(self):
        from tryp.list import List
        return self.cata(lambda v: List(v), List())


class Just(Maybe):

    __slots__ = 'x',

    def __new__(tp, value: A, *args, **kwargs):
        return object.__new__(tp)

    def __init__(self, value):
        self.x = value

    @property
    def _get(self) -> Union[A, None]:
        return self.x

    def __str__(self):
        return 'Just({})'.format(self.x)

    def __repr__(self):
        return 'Just({!r})'.format(self.x)

    def __eq__(self, other):
        if not isinstance(other, Just):
            return False
        return eq(self.x, other.x)


class Empty(Maybe):

    __object = None  # type: Empty

    def __new__(tp, *args, **kwargs):
        if Empty.__object is None:
            Empty.__object = object.__new__(tp)
        return Empty.__object

    def __str__(self):
        return 'Empty()'

    __repr__ = __str__

    def __eq__(self, other):
        return isinstance(other, Empty)


def may(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return Maybe.inst(f(*args, **kwargs))

    return wrapper

__all__ = ['Maybe', 'Just', 'Empty', 'may']
