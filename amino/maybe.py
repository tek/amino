#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x707dc200

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

from typing import TypeVar  # line 1
from typing import Generic  # line 1
from typing import Callable  # line 1
from typing import Union  # line 1
from typing import Any  # line 1
from typing import cast  # line 1
from typing import Optional  # line 1
from typing import Type  # line 1
from typing import Iterator  # line 1
from typing import List as TList  # line 1
from typing import Awaitable  # line 1
from functools import wraps  # line 2
from operator import eq  # line 3
import inspect  # line 4

from amino import boolean  # line 6
from amino.tc.base import F  # line 7
from amino.func import call_by_name  # line 8
from amino.func import I  # line 8
from amino.func import curried  # line 8
from amino.func import CallByName  # line 8

A = TypeVar('A')  # line 10
B = TypeVar('B')  # line 11


class Maybe(Generic[A], F[A], implicits=True):  # line 14

    __slots__ = ()  # line 16

    @_coconut_tco  # line 18
    def __new__(cls, value: 'Optional[A]') -> "'Maybe[A]'":  # line 18
        return _coconut_tail_call(Maybe.check, value)  # line 19

    @staticmethod  # line 21
    def optional(value: 'Optional[A]') -> "'Maybe[A]'":  # line 22
        return Nothing if value is None else Just(value)  # line 23

    @staticmethod  # line 25
    @_coconut_tco  # line 25
    def check(value: 'Optional[A]') -> "'Maybe[A]'":  # line 26
        return _coconut_tail_call(Maybe.optional, value)  # line 27

    @staticmethod  # line 29
    def typed(value: 'Union[A, B]', tpe: 'Type[A]') -> "'Maybe[A]'":  # line 30
        return Just(value) if isinstance(value, tpe) else Nothing  # line 31

    @staticmethod  # line 33
    def wrap(mb: "Union['Maybe[A]', None]") -> "'Maybe[A]'":  # line 34
        return mb if mb is not None and isinstance(mb, Just) else Nothing  # line 35

    @staticmethod  # line 37
    def getattr(obj: 'Any', attr: 'str') -> "'Maybe[A]'":  # line 38
        return Just(getattr(obj, attr)) if hasattr(obj, attr) else Nothing  # line 39

    @staticmethod  # line 41
    @curried  # line 41
    def iff(cond: 'bool', a: 'Union[A, Callable[[], A]]') -> "'Maybe[A]'":  # line 43
        return cast(Maybe, Just(call_by_name(a))) if cond else Nothing  # line 44

    @staticmethod  # line 46
    @curried  # line 46
    def iff_m(cond: 'bool', a: "Union['Maybe[A]', Callable[[], 'Maybe[A]']]") -> "'Maybe[A]'":  # line 48
        return cast(Maybe, call_by_name(a)) if cond else Nothing  # line 49

    @property  # line 51
    def _get(self) -> 'Union[A, None]':  # line 52
        pass  # line 53

    def cata(self, f: 'Callable[[A], B]', b: 'Union[B, Callable[[], B]]') -> 'B':  # line 55
        return (f(cast(A, self._get)) if self.is_just else call_by_name(b))  # line 56

    def cata_f(self, f: 'Callable[[A], B]', b: 'Callable[[], B]') -> 'B':  # line 62
        return (f(cast(A, self._get)) if self.is_just else b())  # line 63

    def cata_strict(self, f: 'Callable[[A], B]', b: 'B') -> 'B':  # line 69
        return (f(cast(A, self._get)) if self.is_just else b)  # line 70

    @_coconut_tco  # line 76
    def filter(self, f: 'Callable[[A], bool]') -> "'Maybe[A]'":  # line 76
        return _coconut_tail_call(self.flat_map, lambda a: self if f(a) else Nothing)  # line 77

    @_coconut_tco  # line 79
    def get_or_else(self, a: 'Union[A, Callable[[], A]]') -> 'A':  # line 79
        return _coconut_tail_call(self.cata, cast(Callable, I), a)  # line 80

    __or__ = get_or_else  # line 82

    @_coconut_tco  # line 84
    def get_or_raise(self, e: 'CallByName') -> 'A':  # line 84
        def raise_e() -> 'None':  # line 85
            raise call_by_name(e)  # line 86
        return _coconut_tail_call(self.cata, cast(Callable, I), raise_e)  # line 87

    @_coconut_tco  # line 89
    def get_or_fail(self, err: 'CallByName') -> 'A':  # line 89
        return _coconut_tail_call(self.get_or_raise, lambda: Exception(call_by_name(err)))  # line 90

    @_coconut_tco  # line 92
    def __contains__(self, v: 'A') -> 'boolean.Boolean':  # line 92
        return _coconut_tail_call(self.contains, v)  # line 93

    def error(self, f: 'Callable[[], Any]') -> "'Maybe[A]'":  # line 95
        self.cata(cast(Callable, I), f)  # line 96
        return self  # line 97

    def observe(self, f: 'Callable[[A], Any]') -> "'Maybe[A]'":  # line 99
        self.foreach(f)  # line 100
        return self  # line 101

    effect = observe  # line 103

    @_coconut_tco  # line 105
    def __iter__(self) -> 'Iterator':  # line 105
        return _coconut_tail_call(iter, self.to_list)  # line 106

    @property  # line 108
    @_coconut_tco  # line 108
    def is_just(self) -> 'boolean.Boolean':  # line 109
        return _coconut_tail_call(boolean.Boolean, isinstance(self, Just))  # line 110

    @property  # line 112
    def is_empty(self) -> 'boolean.Boolean':  # line 113
        return ~self.is_just  # line 114

    empty = is_empty  # line 116

    @property  # line 118
    @_coconut_tco  # line 118
    def to_list(self) -> 'TList[A]':  # line 119
        from amino.list import List  # line 120
        from amino.list import Nil  # line 120
        return _coconut_tail_call(self.cata, List, Nil)  # line 121

    @property  # line 123
    async def unsafe_await(self) -> "'Maybe[Awaitable]'":  # line 124
        if self.is_just:  # line 125
            ret = await cast(Callable[[], Awaitable], self._get)()  # line 126
            return Maybe(ret)  # line 127
        else:  # line 128
            return cast(Maybe[Awaitable], self)  # line 129

    @property  # line 131
    @_coconut_tco  # line 131
    def contains_coro(self) -> 'boolean.Boolean':  # line 132
        return _coconut_tail_call(self.exists, inspect.iscoroutine)  # line 133

    @property  # line 135
    @_coconut_tco  # line 135
    def json_repr(self) -> 'Optional[A]':  # line 136
        return _coconut_tail_call(self.cata, cast(Callable, I), lambda: None)  # line 137


class Just(_coconut_NamedTuple("Just", [("x", 'A')]), Generic[A], Maybe[A]):  # line 140
    __slots__ = ()  # line 140
    __ne__ = _coconut.object.__ne__  # line 140
    @property  # line 140
    def _get(self) -> 'Optional[A]':  # line 143
        return self.x  # line 144

    @_coconut_tco  # line 146
    def __str__(self) -> 'str':  # line 146
        return _coconut_tail_call('Just({!s})'.format, self.x)  # line 147

    @_coconut_tco  # line 149
    def __repr__(self) -> 'str':  # line 149
        return _coconut_tail_call('Just({!r})'.format, self.x)  # line 150

    @_coconut_tco  # line 152
    def __hash__(self) -> 'int':  # line 152
        return _coconut_tail_call(hash, self.x)  # line 153


class _Nothing(Generic[A], Maybe[A]):  # line 156

    __instance: 'Optional[_Nothing]' = None  # line 158

    @_coconut_tco  # line 160
    def __new__(cls: "Type['_Nothing']", *args: 'Any', **kwargs: 'Any') -> "'_Nothing[A]'":  # line 160
        if _Nothing.__instance is None:  # line 161
            _Nothing.__instance = object.__new__(cls)  # line 162
        return _coconut_tail_call(cast, _Nothing, _Nothing.__instance)  # line 163

    def __str__(self) -> 'str':  # line 165
        return 'Nothing'  # line 166

    __repr__ = __str__  # line 168

    @_coconut_tco  # line 170
    def __eq__(self, other: 'Any') -> 'bool':  # line 170
        return _coconut_tail_call(isinstance, other, _Nothing)  # line 171

    @_coconut_tco  # line 173
    def __hash__(self) -> 'int':  # line 173
        return _coconut_tail_call(hash, 'Nothing')  # line 174

Empty = _Nothing  # line 176
Nothing: Maybe = _Nothing()  # line 177


def may(f: 'Callable[..., Optional[A]]') -> 'Callable[..., Maybe[A]]':  # line 180
    @wraps(f)  # line 181
    @_coconut_tco  # line 181
    def wrapper(*a: 'Any', **kw: 'Any') -> 'Maybe[A]':  # line 182
        return _coconut_tail_call(Maybe.check, f(*a, **kw))  # line 183
    return wrapper  # line 184


def flat_may(f: 'Callable[..., Maybe[A]]') -> 'Callable[..., Maybe[A]]':  # line 187
    @wraps(f)  # line 188
    def wrapper(*a: 'Any', **kw: 'Any') -> 'Maybe[A]':  # line 189
        res = f(*a, **kw)  # line 190
        return res if isinstance(res, Maybe) else Nothing  # line 191
    return wrapper  # line 192

__all__ = ('Maybe', 'Just', 'Nothing')  # line 194
