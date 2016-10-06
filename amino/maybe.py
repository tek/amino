from typing import TypeVar, Generic, Callable, Union, Any
from typing import Tuple  # NOQA
from functools import wraps, partial
from operator import eq, is_not
import inspect
import traceback

from fn.op import identity

from amino.logging import log
from amino import boolean
from amino.tc.base import Implicits
from amino.func import call_by_name

A = TypeVar('A')
B = TypeVar('B')


class Maybe(Generic[A], Implicits, implicits=True):

    __slots__ = ()

    def __new__(tp, value: A, checker=partial(is_not, None)):
        return Maybe.check(value, checker)

    @staticmethod
    def check(value: A, checker=partial(is_not, None)):
        return Just(value) if checker(value) else Empty()

    @staticmethod
    def from_call(f: Callable[..., A], *args, **kwargs):
        exc = kwargs.pop('exc', Exception)
        try:
            return Maybe.check(f(*args, **kwargs))
        except exc:
            if exc == Exception:
                frame = inspect.currentframe().f_back  # type: ignore
                stack = traceback.format_stack(frame)
                log.exception('Maybe.from_call:')
                log.error(''.join(stack))
            return Empty()

    @staticmethod
    def typed(value: A, tpe: type):
        return Maybe.check(value, lambda a: isinstance(a, tpe))

    @staticmethod
    def wrap(mb: Union['Maybe[A]', None]):
        return mb if mb is not None and isinstance(mb, Just) else Empty()

    @property
    def _get(self) -> Union[A, None]:
        pass

    def cata(self, f: Callable[[A], B], b: Union[B, Callable[[], B]]) -> B:
        return (
            f(self._get)  # type: ignore
            if self.is_just
            else call_by_name(b)
        )

    def filter(self, f: Callable[[A], B]):
        l = lambda a: self if f(a) else Empty()
        return self.flat_map(l)

    def get_or_else(self, a: Union[A, Callable[[], A]]):
        return self.cata(identity, a)

    __or__ = get_or_else

    def get_or_raise(self, e: Exception):
        def raise_e():
            raise e
        return self.cata(identity, raise_e)

    def get_or_fail(self, err):
        return self.get_or_raise(Exception(call_by_name(err)))

    def __contains__(self, v):
        return self.contains(v)

    def foreach(self, f: Callable[[A], Any]):
        self.cata(f, None)

    def error(self, f: Callable[[], Any]) -> 'Maybe[A]':
        self.cata(identity, f)
        return self

    def observe(self, f: Callable[[A], Any]):
        self.foreach(f)
        return self

    effect = observe

    def debug(self, prefix=None):
        prefix = '' if prefix is None else prefix + ' '
        self.observe(lambda a: log.debug(prefix + str(a)))

    def __iter__(self):
        return iter(self.to_list)

    @property
    def is_just(self):
        return boolean.Boolean(isinstance(self, Just))

    @property
    def is_empty(self):
        return not self.is_just

    empty = is_empty

    def __nonzero__(self):
        return self.is_just

    @property
    def to_list(self):
        from amino.list import List
        return self.cata(lambda v: List(v), List())

    @property
    async def unsafe_await(self):
        if self.is_just:
            ret = await self._get()
            return Maybe(ret)
        else:
            return self

    async def unsafe_await_or(self, b: Union[B, Callable[[], B]]):
        return (Maybe(await(self._get)) if self.is_just  # type: ignore
                else call_by_name(b))

    @property
    def contains_coro(self):
        return self.exists(inspect.iscoroutine)


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
        return 'Just({!s})'.format(self.x)

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
        return Maybe.check(f(*args, **kwargs))
    return wrapper


def flat_may(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        res = f(*args, **kwargs)
        return res if isinstance(res, Maybe) else Maybe(res)
    return wrapper

__all__ = ('Maybe', 'Just', 'Empty', 'may')
