#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xb8c924e2

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

import abc  # line 1
import importlib  # line 2
from typing import TypeVar  # line 3
from typing import Generic  # line 3
from typing import Union  # line 3
from typing import Any  # line 3
from typing import cast  # line 3
from typing import Iterator  # line 3
from typing import Type  # line 3
from types import ModuleType  # line 4
from pathlib import Path  # line 5

import amino  # line 7
from amino import boolean  # line 8
from amino.func import I  # line 9
from amino.tc.base import F  # line 10
from amino.util.mod import unsafe_import_name  # line 11
from amino.tc.monoid import Monoid  # line 12
from amino.tc.monad import Monad  # line 13
from amino.util.string import ToStr  # line 14
from amino.do import do  # line 15
from amino.do import Do  # line 15
from amino.util.exception import format_exception  # line 16

A = TypeVar('A')  # line 18
B = TypeVar('B')  # line 19
C = TypeVar('C')  # line 20
D = TypeVar('D')  # line 21
E = TypeVar('E', bound=Exception)  # line 22


class ImportFailure(ToStr):  # line 25

    @abc.abstractproperty  # line 27
    def expand(self) -> 'amino.List[str]':  # line 28
        ...  # line 29


class ImportException(ImportFailure):  # line 32

    def __init__(self, desc: 'str', exc: 'Exception') -> 'None':  # line 34
        self.desc = desc  # line 35
        self.exc = exc  # line 36

    @_coconut_tco  # line 38
    def _arg_desc(self) -> 'amino.List[str]':  # line 38
        return _coconut_tail_call(amino.List, self.desc, str(self.exc))  # line 39

    @property  # line 41
    @_coconut_tco  # line 41
    def expand(self) -> 'amino.List[str]':  # line 42
        return _coconut_tail_call(format_exception(self.exc).cons, self.desc)  # line 43


class InvalidLocator(ImportFailure):  # line 46

    def __init__(self, msg: 'str') -> 'None':  # line 48
        self.msg = msg  # line 49

    @_coconut_tco  # line 51
    def _arg_desc(self) -> 'amino.List[str]':  # line 51
        return _coconut_tail_call(amino.List, self.msg)  # line 52

    @property  # line 54
    @_coconut_tco  # line 54
    def expand(self) -> 'amino.List[str]':  # line 55
        return _coconut_tail_call(amino.List, self.msg)  # line 56


class Either(Generic[A, B], F[B], implicits=True):  # line 59

    @staticmethod  # line 61
    @_coconut_tco  # line 61
    def import_name(mod: 'str', name: 'str') -> 'Either[ImportFailure, B]':  # line 62
        try:  # line 63
            value = (__builtins__[name] if mod == '__builtins__' else unsafe_import_name(mod, name))  # line 64
        except Exception as e:  # line 69
            return _coconut_tail_call(Left, ImportException(f'{mod}.{name}', e))  # line 70
        else:  # line 71
            return Left(InvalidLocator(f'{mod} has no attribute {name}')) if value is None else Right(value)  # line 72

    @staticmethod  # line 74
    def import_path(path: 'str') -> 'Either[ImportFailure, B]':  # line 75
        from amino.list import List  # line 76
        return (List.wrap(path.rsplit('.', 1)).lift_all(0, 1).to_either(InvalidLocator(f'invalid module path: {path}')).flat_map2(lambda a, b: Either.import_name(a, b).lmap(lambda c: ImportException(path, c))))  # line 77

    @staticmethod  # line 84
    @_coconut_tco  # line 84
    def import_module(modname: 'str') -> 'Either[ImportFailure, ModuleType]':  # line 85
        try:  # line 86
            mod = importlib.import_module(modname)  # line 87
        except Exception as e:  # line 88
            return _coconut_tail_call(Left, ImportException(modname, e))  # line 89
        else:  # line 90
            return _coconut_tail_call(Right, mod)  # line 91

    @staticmethod  # line 93
    @_coconut_tco  # line 93
    def import_file(path: 'Path') -> 'Either[ImportFailure, ModuleType]':  # line 94
        from amino.maybe import Maybe  # line 95
        def step2(spec: 'importlib._bootstrap.ModuleSpec') -> 'ModuleType':  # line 96
            module = importlib.util.module_from_spec(spec)  # line 97
            spec.loader.exec_module(module)  # line 98
            return module  # line 99
        try:  # line 100
            module = Maybe.check(importlib.util.spec_from_file_location('temp', str(path))) / step2  # line 101
        except Exception as e:  # line 102
            return _coconut_tail_call(Left, ImportException(str(path), e))  # line 103
        else:  # line 104
            return _coconut_tail_call(module.to_either, InvalidLocator(f'failed to import `{path}`'))  # line 105

    @staticmethod  # line 107
    @_coconut_tco  # line 107
    def import_from_file(path: 'Path', name: 'str') -> "'Either[ImportFailure, B]'":  # line 108
        @do(Either[ImportFailure, B])  # line 109
        def run() -> 'Do':  # line 110
            module = yield Either.import_file(path)  # line 111
            attr = getattr(module, name, None)  # line 112
            yield (Left(InvalidLocator(f'{path} has no attribute {name}')) if attr is None else Right(attr))  # line 113
        return _coconut_tail_call(run)  # line 118

    @staticmethod  # line 120
    @_coconut_tco  # line 120
    def catch(f: '_coconut.typing.Callable[[], B]', exc: 'Type[E]') -> 'Either[E, B]':  # line 121
        try:  # line 122
            return Right(f())  # line 123
        except exc as e:  # line 124
            return _coconut_tail_call(Left, e)  # line 125

    @staticmethod  # line 127
    @_coconut_tco  # line 127
    def exports(modpath: 'str') -> "'Either[ImportFailure, amino.List[Any]]'":  # line 128
        @do(Either[ImportFailure, amino.List[Any]])  # line 129
        def run() -> 'Do':  # line 130
            from amino.list import Lists  # line 131
            exports = yield Either.import_name(modpath, '__all__')  # line 132
            yield Lists.wrap(exports).traverse(lambda a: Either.import_name(modpath, a), Either)  # line 133
        return _coconut_tail_call(run)  # line 134

    @property  # line 136
    @_coconut_tco  # line 136
    def is_right(self) -> 'amino.Boolean':  # line 137
        return _coconut_tail_call(boolean.Boolean, isinstance(self, Right))  # line 138

    @property  # line 140
    @_coconut_tco  # line 140
    def is_left(self) -> 'amino.Boolean':  # line 141
        return _coconut_tail_call(boolean.Boolean, isinstance(self, Left))  # line 142

    @property  # line 144
    @_coconut_tco  # line 144
    def __left_value(self) -> 'A':  # line 145
        return _coconut_tail_call(cast, A, self.value)  # line 146

    @property  # line 148
    @_coconut_tco  # line 148
    def __right_value(self) -> 'B':  # line 149
        return _coconut_tail_call(cast, B, self.value)  # line 150

    def leffect(self, f: '_coconut.typing.Callable[[A], Any]') -> 'Either[A, B]':  # line 152
        if self.is_left:  # line 153
            f(self.__left_value)  # line 154
        return self  # line 155

    def bieffect(self, l: '_coconut.typing.Callable[[A], Any]', r: '_coconut.typing.Callable[[B], Any]') -> 'Either[A, B]':  # line 157
        self.cata(l, r)  # line 158
        return self  # line 159

    def cata(self, fl: '_coconut.typing.Callable[[A], C]', fr: '_coconut.typing.Callable[[B], C]') -> 'C':  # line 161
        return fl(self.__left_value) if self.is_left else fr(self.__right_value)  # line 162

    def bimap(self, fl: '_coconut.typing.Callable[[A], C]', fr: '_coconut.typing.Callable[[B], D]') -> 'Either[C, D]':  # line 164
        return Left(fl(self.__left_value)) if self.is_left else Right(fr(self.__right_value))  # line 165

    @_coconut_tco  # line 167
    def recover_with(self, f: '_coconut.typing.Callable[[A], Either[C, B]]') -> 'Either[C, B]':  # line 167
        return _coconut_tail_call(self.cata, f, Right)  # line 168

    @_coconut_tco  # line 170
    def right_or_map(self, f: '_coconut.typing.Callable[[A], C]') -> 'C':  # line 170
        return _coconut_tail_call(self.cata, f, I)  # line 171

    @_coconut_tco  # line 173
    def value_or(self, f: '_coconut.typing.Callable[[A], B]') -> 'B':  # line 173
        return _coconut_tail_call(self.cata, f, I)  # line 174

    @_coconut_tco  # line 176
    def left_or(self, f: '_coconut.typing.Callable[[B], A]') -> 'A':  # line 176
        return _coconut_tail_call(self.cata, I, f)  # line 177

    @_coconut_tco  # line 179
    def left_or_map(self, f: '_coconut.typing.Callable[[B], A]') -> 'A':  # line 179
        return _coconut_tail_call(self.cata, I, f)  # line 180

    @property  # line 182
    @_coconut_tco  # line 182
    def ljoin(self) -> 'Either[A, C]':  # line 183
        return _coconut_tail_call(self.right_or_map, Left)  # line 184

    @_coconut_tco  # line 186
    def __str__(self) -> 'str':  # line 186
        return _coconut_tail_call('{}({})'.format, self.__class__.__name__, self.value)  # line 187

    @_coconut_tco  # line 189
    def __repr__(self) -> 'str':  # line 189
        return _coconut_tail_call('{}({!r})'.format, self.__class__.__name__, self.value)  # line 190

    @property  # line 192
    def to_list(self) -> 'amino.List[B]':  # line 193
        return self.to_maybe.to_list  # line 194

    def lmap(self, f: '_coconut.typing.Callable[[A], C]') -> 'Either[C, B]':  # line 196
        return cast(Either, Left(f(self.__left_value))) if self.is_left else cast(Either, Right(self.__right_value))  # line 197

    @_coconut_tco  # line 199
    def get_or_raise(self) -> 'B':  # line 199
        def fail(err: 'A') -> 'B':  # line 200
            raise err if isinstance(err, Exception) else Exception(err)  # line 201
        return _coconut_tail_call(self.cata, fail, I)  # line 202

    @property  # line 204
    @_coconut_tco  # line 204
    def fatal(self) -> 'B':  # line 205
        return _coconut_tail_call(self.get_or_raise)  # line 206

    @_coconut_tco  # line 208
    def __iter__(self) -> 'Iterator[B]':  # line 208
        return _coconut_tail_call(iter, self.to_list)  # line 209

    @property  # line 211
    @_coconut_tco  # line 211
    def swap(self) -> 'Either[B, A]':  # line 212
        return _coconut_tail_call(self.cata, Right, Left)  # line 213

    @property  # line 215
    def json_repr(self) -> 'B':  # line 216
        return self.to_maybe.json_repr  # line 217

    @_coconut_tco  # line 219
    def accum_error(self, b: 'Either[A, C]') -> 'Either[A, C]':  # line 219
        return _coconut_tail_call(self.accum_error_f, lambda: b)  # line 220

    @_coconut_tco  # line 222
    def accum_error_f(self, f: '_coconut.typing.Callable[[], Either[A, C]]', *a, **kw) -> 'Either[A, C]':  # line 222
        _coconut_match_to = self  # line 223
        _coconut_match_check = False  # line 223
        if (_coconut.isinstance(_coconut_match_to, Left)) and (_coconut.len(_coconut_match_to) == 1):  # line 223
            value = _coconut_match_to[0]  # line 223
            _coconut_match_check = True  # line 223
        if _coconut_match_check:  # line 223
            _coconut_match_to = f(*a, **kw)  # line 223
            _coconut_match_check = False  # line 223
            if (_coconut.isinstance(_coconut_match_to, Left)) and (_coconut.len(_coconut_match_to) == 1):  # line 223
                err = _coconut_match_to[0]  # line 223
                _coconut_match_check = True  # line 223
            if _coconut_match_check:  # line 223
                monoid = Monoid.fatal_for(value)  # line 227
                return _coconut_tail_call(Left, monoid.combine(value, err))  # line 228
            if not _coconut_match_check:  # line 229
                r = _coconut_match_to  # line 229
                _coconut_match_check = True  # line 229
                if _coconut_match_check:  # line 229
                    return r  # line 230
        if not _coconut_match_check:  # line 231
            r = _coconut_match_to  # line 231
            _coconut_match_check = True  # line 231
            if _coconut_match_check:  # line 231
                return r  # line 232
# def acc(v: A) -> Either[A, C]:
#     monoid = Monoid.fatal_for(self.__left_value)
#     return monoid.combine(self.__left_value, v)
# return f(*a, **kw).lmap(acc) if self.is_left else self

    @_coconut_tco  # line 238
    def accum_error_lift(self, f: '_coconut.typing.Callable[[], Either[A, C]]', *a, **kw) -> 'Either[A, C]':  # line 238
        _coconut_match_to = self  # line 239
        _coconut_match_check = False  # line 239
        if (_coconut.isinstance(_coconut_match_to, Left)) and (_coconut.len(_coconut_match_to) == 1):  # line 239
            value = _coconut_match_to[0]  # line 239
            _coconut_match_check = True  # line 239
        if _coconut_match_check:  # line 239
            _coconut_match_to = f(*a, **kw)  # line 239
            _coconut_match_check = False  # line 239
            if (_coconut.isinstance(_coconut_match_to, Left)) and (_coconut.len(_coconut_match_to) == 1):  # line 239
                err = _coconut_match_to[0]  # line 239
                _coconut_match_check = True  # line 239
            if _coconut_match_check:  # line 239
                monoid = Monoid.fatal_for(value)  # line 243
                monad = Monad.fatal_for(value)  # line 244
                return _coconut_tail_call(Left, monoid.combine(self.__left_value, monad.pure(err)))  # line 245
            if not _coconut_match_check:  # line 246
                r = _coconut_match_to  # line 246
                _coconut_match_check = True  # line 246
                if _coconut_match_check:  # line 246
                    return r  # line 247
        if not _coconut_match_check:  # line 248
            r = _coconut_match_to  # line 248
            _coconut_match_check = True  # line 248
            if _coconut_match_check:  # line 248
                return r  # line 249
# def acc(v: A) -> Either[A, C]:
#     monoid = Monoid.fatal_for(self.__left_value)
#     monad = Monad.fatal_for(self.__left_value)
#     return monoid.combine(self.__left_value, monad.pure(v))
# return f(*a, **kw).lmap(acc) if self.is_left else self

    def filter_with(self, f: '_coconut.typing.Callable[[B], bool]', g: '_coconut.typing.Callable[[B], C]') -> 'Either[C, B]':  # line 256
        return self // (lambda a: Right(a) if f(a) else Left(g(a)))  # line 257

    @_coconut_tco  # line 259
    def left_contains(self, a: 'A') -> 'boolean.Boolean':  # line 259
        return _coconut_tail_call(boolean.Boolean, self.is_left and self.__left_value == a)  # line 260


class Right(_coconut.collections.namedtuple("Right", "value"), Generic[A, B], Either[A, B]):  # line 263
    __slots__ = ()  # line 263
    __ne__ = _coconut.object.__ne__  # line 263
    def __eq__(self, other: 'Any') -> 'bool':  # line 265
        return isinstance(other, Right) and self._Either__right_value == other._Either__right_value  # line 266


class Left(_coconut.collections.namedtuple("Left", "value"), Generic[A, B], Either[A, B]):  # line 269
    __slots__ = ()  # line 269
    __ne__ = _coconut.object.__ne__  # line 269
    def __eq__(self, other: 'Any') -> 'bool':  # line 271
        return isinstance(other, Left) and self._Either__left_value == other._Either__left_value  # line 272


@_coconut_tco  # line 275
def Try(f: '_coconut.typing.Callable[[], A]', *a: 'Any', **kw: 'Any') -> 'Either[Exception, A]':  # line 275
    try:  # line 276
        return Right(f(*a, **kw))  # line 277
    except Exception as e:  # line 278
        return _coconut_tail_call(Left, e)  # line 279


__all__ = ('Either', 'Left', 'Right', 'ImportFailure', 'ImportException', 'InvalidLocator', 'Try')  # line 282
