from typing import TypeVar, Generic, Callable, Union, Any
from typing import Tuple  # NOQA
from functools import wraps, partial
from operator import eq, is_not
import inspect
import traceback

from fn import _
from fn.op import identity

from tryp.logging import log
from tryp.tc.base import Implicits, ImplicitInstances, tc_prop
from tryp.lazy import lazy
from tryp.tc.monad import Monad
from tryp.tc.optional import Optional

A = TypeVar('A')
B = TypeVar('B')


class MaybeInstances(ImplicitInstances):

    @lazy
    def _instances(self):
        from tryp import Map
        return Map({Monad: MaybeMonad(), Optional: MaybeOptional()})


class Maybe(Generic[A], Implicits, implicits=True):

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
            if exc == Exception:
                stack = traceback.format_stack(inspect.currentframe().f_back)
                log.exception('Maybe.from_call:')
                log.error(''.join(stack))
            return Empty()

    @staticmethod
    def typed(value: A, tpe: type):
        return Maybe.inst(value, lambda a: isinstance(a, tpe))

    @staticmethod
    def wrap(mb: Union['Maybe[A]', None]):
        return mb if mb is not None and isinstance(mb, Just) else Empty()

    @property
    def _get(self) -> Union[A, None]:
        pass

    def _call_by_name(self, b: Union[B, Callable[[], B]]):
        if isinstance(b, Callable):  # type: ignore
            return b()  # type: ignore
        else:
            return b  # type: ignore

    def cata(self, f: Callable[[A], B], b: Union[B, Callable[[], B]]) -> B:
        return f(self._get) if self.is_just else self._call_by_name(b)

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

    def get_or_raise(self, e: Exception):
        def raise_e():
            raise e
        return self.cata(identity, raise_e)

    def exists(self, f: Callable[[A], bool]):
        return self.cata(f, False)

    def contains(self, v):
        return self.exists(_ == v)

    def __contains__(self, v):
        return self.contains(v)

    def zip(self, other: 'Maybe[B]') -> 'Maybe[Tuple[A, B]]':
        if self.is_just and other.is_just:
            return Just((self._get, other._get))
        else:
            return Empty()

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
        return (isinstance(self, Just))

    @property
    def is_empty(self):
        return not self.is_just

    def __nonzero__(self):
        return self.is_just

    @property
    def to_list(self):
        from tryp.list import List
        return self.cata(lambda v: List(v), List())

    def replace(self, b: B):
        return self.map(lambda a: b)

    @property
    async def unsafe_await(self):
        if self.is_just:
            ret = await self._get()
            return Maybe(ret)
        else:
            return self

    async def unsafe_await_or(self, b: Union[B, Callable[[], B]]):
        return (Maybe(await(self._get)) if self.is_just else
                self._call_by_name(b))

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


class MaybeMonad(Monad):

    def pure(self, a: A):
        return Just(a)

    def flat_map(self, fa: Maybe[A], f: Callable[[A], Maybe[B]]) -> Maybe[B]:
        return fa.cata(lambda v: f(v), Empty())


class MaybeOptional(Optional):

    @tc_prop
    def to_maybe(self, fa: Maybe):
        return fa

    def to_either(self, fa: Maybe, left):
        from tryp.either import Left, Right
        return fa.cata(Right, lambda: Left(left))

__all__ = ('Maybe', 'Just', 'Empty', 'may')
