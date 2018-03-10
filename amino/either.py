#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x6bbc9d9a

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
from typing import Generator  # line 3
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
            value = unsafe_import_name(mod, name)  # line 64
        except Exception as e:  # line 65
            return _coconut_tail_call(Left, ImportException(f'{mod}.{name}', e))  # line 66
        else:  # line 67
            return Left(InvalidLocator(f'{mod} has no attribute {name}')) if value is None else Right(value)  # line 68

    @staticmethod  # line 70
    def import_path(path: 'str') -> 'Either[ImportFailure, B]':  # line 71
        from amino.list import List  # line 72
        return (List.wrap(path.rsplit('.', 1)).lift_all(0, 1).to_either(InvalidLocator(f'invalid module path: {path}')).flat_map2(lambda a, b: Either.import_name(a, b).lmap(lambda c: ImportException(path, c))))  # line 73

    @staticmethod  # line 80
    @_coconut_tco  # line 80
    def import_module(modname: 'str') -> 'Either[ImportFailure, ModuleType]':  # line 81
        try:  # line 82
            mod = importlib.import_module(modname)  # line 83
        except Exception as e:  # line 84
            return _coconut_tail_call(Left, ImportException(modname, e))  # line 85
        else:  # line 86
            return _coconut_tail_call(Right, mod)  # line 87

    @staticmethod  # line 89
    @_coconut_tco  # line 89
    def import_file(path: 'Path') -> 'Either[ImportFailure, ModuleType]':  # line 90
        from amino.maybe import Maybe  # line 91
        def step2(spec: 'importlib._bootstrap.ModuleSpec') -> 'ModuleType':  # line 92
            module = importlib.util.module_from_spec(spec)  # line 93
            spec.loader.exec_module(module)  # line 94
            return module  # line 95
        try:  # line 96
            module = Maybe.check(importlib.util.spec_from_file_location('temp', str(path))) / step2  # line 97
        except Exception as e:  # line 98
            return _coconut_tail_call(Left, ImportException(str(path), e))  # line 99
        else:  # line 100
            return _coconut_tail_call(module.to_either, InvalidLocator(f'failed to import `{path}`'))  # line 101

    @staticmethod  # line 103
    @do('Either[ImportFailure, B]')  # line 103
    def import_from_file(path: 'Path', name: 'str') -> 'Generator':  # line 105
        module = yield Either.import_file(path)  # line 106
        attr = getattr(module, name, None)  # line 107
        yield (Left(InvalidLocator(f'{path} has no attribute {name}')) if attr is None else Right(attr))  # line 108

    @staticmethod  # line 114
    @_coconut_tco  # line 114
    def catch(f: '_coconut.typing.Callable[[], B]', exc: 'Type[E]') -> 'Either[E, B]':  # line 115
        try:  # line 116
            return Right(f())  # line 117
        except exc as e:  # line 118
            return _coconut_tail_call(Left, e)  # line 119

    @staticmethod  # line 121
    @do('Either[ImportFailure, amino.List[Any]]')  # line 121
    def exports(modpath: 'str') -> 'Generator':  # line 123
        from amino.list import Lists  # line 124
        exports = yield Either.import_name(modpath, '__all__')  # line 125
        yield Lists.wrap(exports).traverse(lambda a: Either.import_name(modpath, a), Either)  # line 126

    @property  # line 128
    @_coconut_tco  # line 128
    def is_right(self) -> 'amino.Boolean':  # line 129
        return _coconut_tail_call(boolean.Boolean, isinstance(self, Right))  # line 130

    @property  # line 132
    @_coconut_tco  # line 132
    def is_left(self) -> 'amino.Boolean':  # line 133
        return _coconut_tail_call(boolean.Boolean, isinstance(self, Left))  # line 134

    @property  # line 136
    @_coconut_tco  # line 136
    def __left_value(self) -> 'A':  # line 137
        return _coconut_tail_call(cast, A, self.value)  # line 138

    @property  # line 140
    @_coconut_tco  # line 140
    def __right_value(self) -> 'B':  # line 141
        return _coconut_tail_call(cast, B, self.value)  # line 142

    def leffect(self, f: '_coconut.typing.Callable[[A], Any]') -> 'Either[A, B]':  # line 144
        if self.is_left:  # line 145
            f(self.__left_value)  # line 146
        return self  # line 147

    def bieffect(self, l: '_coconut.typing.Callable[[A], Any]', r: '_coconut.typing.Callable[[B], Any]') -> 'Either[A, B]':  # line 149
        self.cata(l, r)  # line 150
        return self  # line 151

    def cata(self, fl: '_coconut.typing.Callable[[A], C]', fr: '_coconut.typing.Callable[[B], C]') -> 'C':  # line 153
        return fl(self.__left_value) if self.is_left else fr(self.__right_value)  # line 154

    def bimap(self, fl: '_coconut.typing.Callable[[A], C]', fr: '_coconut.typing.Callable[[B], D]') -> 'Either[C, D]':  # line 156
        return Left(fl(self.__left_value)) if self.is_left else Right(fr(self.__right_value))  # line 157

    @_coconut_tco  # line 159
    def recover_with(self, f: '_coconut.typing.Callable[[A], Either[C, B]]') -> 'Either[C, B]':  # line 159
        return _coconut_tail_call(self.cata, f, Right)  # line 160

    @_coconut_tco  # line 162
    def right_or_map(self, f: '_coconut.typing.Callable[[A], C]') -> 'C':  # line 162
        return _coconut_tail_call(self.cata, f, I)  # line 163

    @_coconut_tco  # line 165
    def value_or(self, f: '_coconut.typing.Callable[[A], B]') -> 'B':  # line 165
        return _coconut_tail_call(self.cata, f, I)  # line 166

    @_coconut_tco  # line 168
    def left_or(self, f: '_coconut.typing.Callable[[B], A]') -> 'A':  # line 168
        return _coconut_tail_call(self.cata, I, f)  # line 169

    @_coconut_tco  # line 171
    def left_or_map(self, f: '_coconut.typing.Callable[[B], A]') -> 'A':  # line 171
        return _coconut_tail_call(self.cata, I, f)  # line 172

    @property  # line 174
    @_coconut_tco  # line 174
    def ljoin(self) -> 'Either[A, C]':  # line 175
        return _coconut_tail_call(self.right_or_map, Left)  # line 176

    @_coconut_tco  # line 178
    def __str__(self) -> 'str':  # line 178
        return _coconut_tail_call('{}({})'.format, self.__class__.__name__, self.value)  # line 179

    @_coconut_tco  # line 181
    def __repr__(self) -> 'str':  # line 181
        return _coconut_tail_call('{}({!r})'.format, self.__class__.__name__, self.value)  # line 182

    @property  # line 184
    def to_list(self) -> 'amino.List[B]':  # line 185
        return self.to_maybe.to_list  # line 186

    def lmap(self, f: '_coconut.typing.Callable[[A], C]') -> 'Either[C, B]':  # line 188
        return cast(Either, Left(f(self.__left_value))) if self.is_left else cast(Either, Right(self.__right_value))  # line 189

    @_coconut_tco  # line 191
    def get_or_raise(self) -> 'B':  # line 191
        def fail(err: 'A') -> 'B':  # line 192
            raise err if isinstance(err, Exception) else Exception(err)  # line 193
        return _coconut_tail_call(self.cata, fail, I)  # line 194

    @property  # line 196
    @_coconut_tco  # line 196
    def fatal(self) -> 'B':  # line 197
        return _coconut_tail_call(self.get_or_raise)  # line 198

    @_coconut_tco  # line 200
    def __iter__(self) -> 'Iterator[B]':  # line 200
        return _coconut_tail_call(iter, self.to_list)  # line 201

    @property  # line 203
    @_coconut_tco  # line 203
    def swap(self) -> 'Either[B, A]':  # line 204
        return _coconut_tail_call(self.cata, Right, Left)  # line 205

    @property  # line 207
    def json_repr(self) -> 'B':  # line 208
        return self.to_maybe.json_repr  # line 209

    @_coconut_tco  # line 211
    def accum_error(self, b: 'Either[A, C]') -> 'Either[A, C]':  # line 211
        return _coconut_tail_call(self.accum_error_f, lambda: b)  # line 212

    @_coconut_tco  # line 214
    def accum_error_f(self, f: '_coconut.typing.Callable[[], Either[A, C]]', *a, **kw) -> 'Either[A, C]':  # line 214
        _coconut_match_to = self  # line 215
        _coconut_match_check = False  # line 215
        if (_coconut.isinstance(_coconut_match_to, Left)) and (_coconut.len(_coconut_match_to) == 1):  # line 215
            value = _coconut_match_to[0]  # line 215
            _coconut_match_check = True  # line 215
        if _coconut_match_check:  # line 215
            _coconut_match_to = f(*a, **kw)  # line 215
            _coconut_match_check = False  # line 215
            if (_coconut.isinstance(_coconut_match_to, Left)) and (_coconut.len(_coconut_match_to) == 1):  # line 215
                err = _coconut_match_to[0]  # line 215
                _coconut_match_check = True  # line 215
            if _coconut_match_check:  # line 215
                monoid = Monoid.fatal_for(value)  # line 219
                return _coconut_tail_call(Left, monoid.combine(value, err))  # line 220
            if not _coconut_match_check:  # line 221
                r = _coconut_match_to  # line 221
                _coconut_match_check = True  # line 221
                if _coconut_match_check:  # line 221
                    return r  # line 222
        if not _coconut_match_check:  # line 223
            r = _coconut_match_to  # line 223
            _coconut_match_check = True  # line 223
            if _coconut_match_check:  # line 223
                return r  # line 224
# def acc(v: A) -> Either[A, C]:
#     monoid = Monoid.fatal_for(self.__left_value)
#     return monoid.combine(self.__left_value, v)
# return f(*a, **kw).lmap(acc) if self.is_left else self

    @_coconut_tco  # line 230
    def accum_error_lift(self, f: '_coconut.typing.Callable[[], Either[A, C]]', *a, **kw) -> 'Either[A, C]':  # line 230
        _coconut_match_to = self  # line 231
        _coconut_match_check = False  # line 231
        if (_coconut.isinstance(_coconut_match_to, Left)) and (_coconut.len(_coconut_match_to) == 1):  # line 231
            value = _coconut_match_to[0]  # line 231
            _coconut_match_check = True  # line 231
        if _coconut_match_check:  # line 231
            _coconut_match_to = f(*a, **kw)  # line 231
            _coconut_match_check = False  # line 231
            if (_coconut.isinstance(_coconut_match_to, Left)) and (_coconut.len(_coconut_match_to) == 1):  # line 231
                err = _coconut_match_to[0]  # line 231
                _coconut_match_check = True  # line 231
            if _coconut_match_check:  # line 231
                monoid = Monoid.fatal_for(value)  # line 235
                monad = Monad.fatal_for(value)  # line 236
                return _coconut_tail_call(Left, monoid.combine(self.__left_value, monad.pure(err)))  # line 237
            if not _coconut_match_check:  # line 238
                r = _coconut_match_to  # line 238
                _coconut_match_check = True  # line 238
                if _coconut_match_check:  # line 238
                    return r  # line 239
        if not _coconut_match_check:  # line 240
            r = _coconut_match_to  # line 240
            _coconut_match_check = True  # line 240
            if _coconut_match_check:  # line 240
                return r  # line 241
# def acc(v: A) -> Either[A, C]:
#     monoid = Monoid.fatal_for(self.__left_value)
#     monad = Monad.fatal_for(self.__left_value)
#     return monoid.combine(self.__left_value, monad.pure(v))
# return f(*a, **kw).lmap(acc) if self.is_left else self

    def filter_with(self, f: '_coconut.typing.Callable[[B], bool]', g: '_coconut.typing.Callable[[B], C]') -> 'Either[C, B]':  # line 248
        return self // (lambda a: Right(a) if f(a) else Left(g(a)))  # line 249

    @_coconut_tco  # line 251
    def left_contains(self, a: 'A') -> 'boolean.Boolean':  # line 251
        return _coconut_tail_call(boolean.Boolean, self.is_left and self.__left_value == a)  # line 252


class Right(_coconut.collections.namedtuple("Right", "value"), Generic[A, B], Either[A, B]):  # line 255
    __slots__ = ()  # line 255
    __ne__ = _coconut.object.__ne__  # line 255
    def __eq__(self, other: 'Any') -> 'bool':  # line 257
        return isinstance(other, Right) and self._Either__right_value == other._Either__right_value  # line 258


class Left(_coconut.collections.namedtuple("Left", "value"), Generic[A, B], Either[A, B]):  # line 261
    __slots__ = ()  # line 261
    __ne__ = _coconut.object.__ne__  # line 261
    def __eq__(self, other: 'Any') -> 'bool':  # line 263
        return isinstance(other, Left) and self._Either__left_value == other._Either__left_value  # line 264


@_coconut_tco  # line 267
def Try(f: '_coconut.typing.Callable[[], A]', *a: 'Any', **kw: 'Any') -> 'Either[Exception, A]':  # line 267
    try:  # line 268
        return Right(f(*a, **kw))  # line 269
    except Exception as e:  # line 270
        return _coconut_tail_call(Left, e)  # line 271


__all__ = ('Either', 'Left', 'Right', 'ImportFailure', 'ImportException', 'InvalidLocator', 'Try')  # line 274
