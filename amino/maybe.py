import typing
from typing import TypeVar, Generic, Callable, Union, Any, cast, Optional, Type, Iterator, Awaitable
from functools import wraps
from operator import eq
import inspect

from amino import boolean
from amino.tc.base import F
from amino.func import call_by_name, I, curried, CallByName

A = TypeVar('A')
B = TypeVar('B')


class Maybe(Generic[A], F[A], implicits=True):
    __slots__ = ()

    @staticmethod
    def optional(value: Optional[A]) -> 'Maybe[A]':
        return Nothing if value is None else Just(value)

    @staticmethod
    def check(value: Optional[A]) -> 'Maybe[A]':
        return Maybe.optional(value)

    @staticmethod
    def typed(value: Union[A, B], tpe: Type[A]) -> 'Maybe[A]':
        return Just(value) if isinstance(value, tpe) else Nothing

    @staticmethod
    def wrap(mb: Union['Maybe[A]', None]) -> 'Maybe[A]':
        return mb if mb is not None and isinstance(mb, Just) else Nothing

    @staticmethod
    def getattr(obj: Any, attr: str) -> 'Maybe[A]':
        return Just(getattr(obj, attr)) if hasattr(obj, attr) else Nothing

    @staticmethod
    @curried
    def iff(cond: bool, a: Union[A, Callable[[], A]]) -> 'Maybe[A]':
        return cast(Maybe, Just(call_by_name(a))) if cond else Nothing

    @staticmethod
    @curried
    def iff_m(cond: bool, a: Union['Maybe[A]', Callable[[], 'Maybe[A]']]) -> 'Maybe[A]':
        return cast(Maybe, call_by_name(a)) if cond else Nothing

    @property
    def _get(self) -> Union[A, None]:
        pass

    def cata(self, f: Callable[[A], B], b: Union[B, Callable[[], B]]) -> B:
        return (
            f(cast(A, self._get))
            if self.is_just
            else call_by_name(b)
        )

    def cata_f(self, f: Callable[[A], B], b: Callable[..., B], *a: Any, **kw: Any) -> B:
        return (
            f(cast(A, self._get))
            if self.is_just
            else b(*a, **kw)
        )

    def cata_strict(self, f: Callable[[A], B], b: B) -> B:
        return (
            f(cast(A, self._get))
            if self.is_just
            else b
        )

    def filter(self, f: Callable[[A], bool]) -> 'Maybe[A]':
        return self.flat_map(lambda a: self if f(a) else Nothing)

    def get_or_else(self, a: Union[A, Callable[[], A]]) -> A:
        return self.cata(cast(Callable, I), a)

    __or__ = get_or_else

    def get_or(self, f: Callable[..., A], *a: Any, **kw: Any) -> A:
        return self.cata_f(lambda a: a, f, *a, **kw)

    def get_or_strict(self, a: A) -> A:
        return self.cata_strict(lambda a: a, a)

    def get_or_raise(self, e: CallByName) -> A:
        def raise_e() -> None:
            raise call_by_name(e)
        return self.cata(cast(Callable, I), raise_e)

    def get_or_fail(self, err: CallByName) -> A:
        return self.get_or_raise(lambda: Exception(call_by_name(err)))

    def __contains__(self, v: A) -> boolean.Boolean:
        return self.contains(v)

    def error(self, f: Callable[[], Any]) -> 'Maybe[A]':
        self.cata(cast(Callable, I), f)
        return self

    def observe(self, f: Callable[[A], Any]) -> 'Maybe[A]':
        self.foreach(f)
        return self

    effect = observe

    def __iter__(self) -> Iterator:
        return iter(self.to_list)

    @property
    def is_just(self) -> boolean.Boolean:
        return boolean.Boolean(isinstance(self, Just))

    @property
    def is_empty(self) -> boolean.Boolean:
        return ~self.is_just

    empty = is_empty

    @property
    def to_list(self) -> list:
        from amino.list import List, Nil
        return self.cata(List, Nil)

    @property
    async def unsafe_await(self) -> 'Maybe[Awaitable]':
        if self.is_just:
            ret = await cast(Callable[[], Awaitable], self._get)()
            return Maybe.optional(ret)
        else:
            return cast(Maybe[Awaitable], self)

    @property
    def contains_coro(self) -> boolean.Boolean:
        return self.exists(inspect.iscoroutine)


class Just(Generic[A], Maybe[A]):

    def __init__(self, x: A) -> None:
        self.x = x

    @property
    def _get(self) -> Optional[A]:
        return self.x

    def __str__(self) -> str:
        return 'Just({!s})'.format(self.x)

    def __repr__(self) -> str:
        return 'Just({!r})'.format(self.x)

    def __hash__(self) -> int:
        return hash(self.x)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Just) and other.x == self.x


class _Nothing(Generic[A], Maybe[A]):

    __instance: 'Optional[_Nothing]' = None

    def __new__(cls: Type['_Nothing'], *args: Any, **kwargs: Any) -> '_Nothing[A]':
        if _Nothing.__instance is None:
            _Nothing.__instance = object.__new__(cls)
        return cast(_Nothing, _Nothing.__instance)

    def __str__(self) -> str:
        return 'Nothing'

    __repr__ = __str__

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, _Nothing)

    def __hash__(self) -> int:
        return hash('Nothing')

Empty = _Nothing
Nothing: Maybe = _Nothing()


def may(f: Callable[..., Optional[A]]) -> Callable[..., Maybe[A]]:
    @wraps(f)
    def wrapper(*a: Any, **kw: Any) -> Maybe[A]:
        return Maybe.check(f(*a, **kw))
    return wrapper


def flat_may(f: Callable[..., Maybe[A]]) -> Callable[..., Maybe[A]]:
    @wraps(f)
    def wrapper(*a: Any, **kw: Any) -> Maybe[A]:
        res = f(*a, **kw)
        return res if isinstance(res, Maybe) else Nothing
    return wrapper

__all__ = ('Maybe', 'Just', 'Nothing')
