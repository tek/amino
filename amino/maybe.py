#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xd41c3ed4

# Compiled with Coconut version 1.3.0 [Dead Parrot]

# Coconut Header: -------------------------------------------------------------

from __future__ import generator_stop
import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import _coconut, _coconut_NamedTuple, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_pipe, _coconut_star_pipe, _coconut_back_pipe, _coconut_back_star_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial
from __coconut__ import *
_coconut_sys.path.remove(_coconut_file_path)

# Compiled Coconut: -----------------------------------------------------------

from typing import TypeVar
from typing import Generic
from typing import Callable
from typing import Union
from typing import Any
from typing import cast
from typing import Optional
from typing import Type
from typing import Iterator
from typing import List as TList
from typing import Awaitable
from functools import wraps
from operator import eq
import inspect

from amino import boolean
from amino.tc.base import F
from amino.func import call_by_name
from amino.func import I
from amino.func import curried
from amino.func import CallByName

A = TypeVar('A')
B = TypeVar('B')


class Maybe(Generic[A], F[A], implicits=True):

    __slots__ = ()

    @_coconut_tco
    def __new__(cls, value: 'Optional[A]') -> "'Maybe[A]'":
        return _coconut_tail_call(Maybe.check, value)

    @staticmethod
    def optional(value: 'Optional[A]') -> "'Maybe[A]'":
        return Nothing if value is None else Just(value)

    @staticmethod
    @_coconut_tco
    def check(value: 'Optional[A]') -> "'Maybe[A]'":
        return _coconut_tail_call(Maybe.optional, value)

    @staticmethod
    def typed(value: 'Union[A, B]', tpe: 'Type[A]') -> "'Maybe[A]'":
        return Just(value) if isinstance(value, tpe) else Nothing

    @staticmethod
    def wrap(mb: "Union['Maybe[A]', None]") -> "'Maybe[A]'":
        return mb if mb is not None and isinstance(mb, Just) else Nothing

    @staticmethod
    def getattr(obj: 'Any', attr: 'str') -> "'Maybe[A]'":
        return Just(getattr(obj, attr)) if hasattr(obj, attr) else Nothing

    @staticmethod
    @curried
    def iff(cond: 'bool', a: 'Union[A, Callable[[], A]]') -> "'Maybe[A]'":
        return cast(Maybe, Just(call_by_name(a))) if cond else Nothing

    @staticmethod
    @curried
    def iff_m(cond: 'bool', a: "Union['Maybe[A]', Callable[[], 'Maybe[A]']]") -> "'Maybe[A]'":
        return cast(Maybe, call_by_name(a)) if cond else Nothing

    @property
    def _get(self) -> 'Union[A, None]':
        pass

    def cata(self, f: 'Callable[[A], B]', b: 'Union[B, Callable[[], B]]') -> 'B':
        return (f(cast(A, self._get)) if self.is_just else call_by_name(b))

    @_coconut_tco
    def filter(self, f: 'Callable[[A], bool]') -> "'Maybe[A]'":
        return _coconut_tail_call(self.flat_map, lambda a: self if f(a) else Nothing)

    @_coconut_tco
    def get_or_else(self, a: 'Union[A, Callable[[], A]]') -> 'A':
        return _coconut_tail_call(self.cata, cast(Callable, I), a)

    __or__ = get_or_else

    @_coconut_tco
    def get_or_raise(self, e: 'CallByName') -> 'A':
        def raise_e() -> 'None':
            raise call_by_name(e)
        return _coconut_tail_call(self.cata, cast(Callable, I), raise_e)

    @_coconut_tco
    def get_or_fail(self, err: 'CallByName') -> 'A':
        return _coconut_tail_call(self.get_or_raise, lambda: Exception(call_by_name(err)))

    @_coconut_tco
    def __contains__(self, v: 'A') -> 'boolean.Boolean':
        return _coconut_tail_call(self.contains, v)

    def error(self, f: 'Callable[[], Any]') -> "'Maybe[A]'":
        self.cata(cast(Callable, I), f)
        return self

    def observe(self, f: 'Callable[[A], Any]') -> "'Maybe[A]'":
        self.foreach(f)
        return self

    effect = observe

    @_coconut_tco
    def __iter__(self) -> 'Iterator':
        return _coconut_tail_call(iter, self.to_list)

    @property
    @_coconut_tco
    def is_just(self) -> 'boolean.Boolean':
        return _coconut_tail_call(boolean.Boolean, isinstance(self, Just))

    @property
    def is_empty(self) -> 'boolean.Boolean':
        return ~self.is_just

    empty = is_empty

    @property
    @_coconut_tco
    def to_list(self) -> 'TList[A]':
        from amino.list import List
        from amino.list import Nil
        return _coconut_tail_call(self.cata, List, Nil)

    @property
    async def unsafe_await(self) -> "'Maybe[Awaitable]'":
        if self.is_just:
            ret = await cast(Callable[[], Awaitable], self._get)()
            return Maybe(ret)
        else:
            return cast(Maybe[Awaitable], self)

    @property
    @_coconut_tco
    def contains_coro(self) -> 'boolean.Boolean':
        return _coconut_tail_call(self.exists, inspect.iscoroutine)

    @property
    @_coconut_tco
    def json_repr(self) -> 'Optional[A]':
        return _coconut_tail_call(self.cata, cast(Callable, I), lambda: None)


class Just(_coconut_NamedTuple("Just", [("x", 'A')]), Generic[A], Maybe[A]):
    __slots__ = ()
    __ne__ = _coconut.object.__ne__
    @property
    def _get(self) -> 'Optional[A]':
        return self.x

    @_coconut_tco
    def __str__(self) -> 'str':
        return _coconut_tail_call('Just({!s})'.format, self.x)

    @_coconut_tco
    def __repr__(self) -> 'str':
        return _coconut_tail_call('Just({!r})'.format, self.x)

    @_coconut_tco
    def __hash__(self) -> 'int':
        return _coconut_tail_call(hash, self.x)


class _Nothing(Generic[A], Maybe[A]):

    __instance: 'Optional[_Nothing]' = None

    @_coconut_tco
    def __new__(cls: "Type['_Nothing']", *args: 'Any', **kwargs: 'Any') -> "'_Nothing[A]'":
        if _Nothing.__instance is None:
            _Nothing.__instance = object.__new__(cls)
        return _coconut_tail_call(cast, _Nothing, _Nothing.__instance)

    def __str__(self) -> 'str':
        return 'Nothing'

    __repr__ = __str__

    @_coconut_tco
    def __eq__(self, other: 'Any') -> 'bool':
        return _coconut_tail_call(isinstance, other, _Nothing)

    @_coconut_tco
    def __hash__(self) -> 'int':
        return _coconut_tail_call(hash, 'Nothing')

Empty = _Nothing
Nothing: Maybe = _Nothing()


def may(f: 'Callable[..., Optional[A]]') -> 'Callable[..., Maybe[A]]':
    @wraps(f)
    @_coconut_tco
    def wrapper(*a: 'Any', **kw: 'Any') -> 'Maybe[A]':
        return _coconut_tail_call(Maybe.check, f(*a, **kw))
    return wrapper


def flat_may(f: 'Callable[..., Maybe[A]]') -> 'Callable[..., Maybe[A]]':
    @wraps(f)
    def wrapper(*a: 'Any', **kw: 'Any') -> 'Maybe[A]':
        res = f(*a, **kw)
        return res if isinstance(res, Maybe) else Nothing
    return wrapper

__all__ = ('Maybe', 'Just', 'Nothing')
