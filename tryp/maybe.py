from typing import TypeVar, Generic, Callable, Union, Iterable, Any
from typing import Tuple  # NOQA

from functools import wraps, partial  # type: ignore
from operator import eq, is_not  # type: ignore

from fn import F, _  # type: ignore
from fn.op import identity  # type: ignore

A = TypeVar('A')

B = TypeVar('B')


class Maybe(Iterable[A], Generic[A]):

    __slots__ = ()

    def __new__(tp, value: A, checker=partial(is_not, None)):
        return Maybe.inst(value, checker)

    @staticmethod
    def inst(value: A, checker=partial(is_not, None)):
        return Just(value) if checker(value) else Empty()

    @staticmethod
    def from_call(f: Callable[..., A], *args, **kwargs):
        exc = kwargs.pop('exc', Exception)
        try:
            return Maybe.inst(f(*args, **kwargs))
        except exc:
            return Empty()

    @staticmethod
    def typed(value: A, tpe: type):
        return Maybe.inst(value, lambda a: isinstance(a, tpe))

    @property
    def _get(self) -> Union[A, None]:
        pass

    def cata(self, f: Callable[[A], B], b: Union[B, Callable[[], B]]) -> B:
        if self.isJust:
            return f(self._get)
        elif isinstance(b, Callable):  # type: ignore
            return b()  # type: ignore
        else:
            return b  # type: ignore

    def map(self, f: Callable[[A], B]) -> 'Maybe[B]':
        return self.cata(lambda v: Just(f(v)), Empty())

    def smap(self, f: Callable[..., B]) -> 'Maybe[B]':
        return self.cata(lambda v: Just(f(*v)), Empty())  # type: ignore

    def flat_map(self, f: Callable[[A], 'Maybe[B]']) -> 'Maybe[B]':
        e = Empty()  # type: Maybe[B]
        return self.cata(f, e)

    def flat_smap(self, f: Callable[..., 'Maybe[B]']) -> 'Maybe[B]':
        e = Empty()  # type: Maybe[B]
        return self.cata(lambda v: f(*v), e)  # type: ignore

    @property
    def flatten(self):
        return self.flat_map(_)

    def filter(self, f: Callable[[A], B]):
        l = lambda a: self if f(a) else Empty()
        return self.flat_map(l)

    def get_or_else(self, a: Union[A, Callable[[], A]]):
        return self.cata(identity, a)

    __or__ = get_or_else

    def or_else(self, ma: Union['Maybe[A]', Callable[[], 'Maybe[A]']]):
        return self.cata(lambda v: self, ma)

    def exists(self, f: Callable[[A], bool]):
        return self.cata(f, False)

    def contains(self, v):
        return self.exists(_ == v)

    def zip(self, other: 'Maybe[B]') -> 'Maybe[Tuple[A, B]]':
        if self.isJust and other.isJust:
            return Just((self._get, other._get))
        else:
            return Empty()

    def foreach(self, f: Callable[[A], Any]):
        self.cata(f, None)

    def __iter__(self):
        return iter(self.toList)

    @property
    def isJust(self):
        return (isinstance(self, Just))

    def __nonzero__(self):
        return self.isJust

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

    def __hash__(self):
        return hash(self._get)


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

    def __hash__(self):
        return hash('Empty')


def may(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return Maybe.inst(f(*args, **kwargs))
    return wrapper


def flat_may(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        res = f(*args, **kwargs)
        return res if isinstance(res, Maybe) else Maybe(res)
    return wrapper

__all__ = ['Maybe', 'Just', 'Empty', 'may']
