#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xc16bb5f

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
    @_coconut_tco  # line 103
    def import_from_file(path: 'Path', name: 'str') -> "'Either[ImportFailure, B]'":  # line 104
        @do(Either[ImportFailure, B])  # line 105
        def run() -> 'Do':  # line 106
            module = yield Either.import_file(path)  # line 107
            attr = getattr(module, name, None)  # line 108
            yield (Left(InvalidLocator(f'{path} has no attribute {name}')) if attr is None else Right(attr))  # line 109
        return _coconut_tail_call(run)  # line 114

    @staticmethod  # line 116
    @_coconut_tco  # line 116
    def catch(f: '_coconut.typing.Callable[[], B]', exc: 'Type[E]') -> 'Either[E, B]':  # line 117
        try:  # line 118
            return Right(f())  # line 119
        except exc as e:  # line 120
            return _coconut_tail_call(Left, e)  # line 121

    @staticmethod  # line 123
    @_coconut_tco  # line 123
    def exports(modpath: 'str') -> "'Either[ImportFailure, amino.List[Any]]'":  # line 124
        @do(Either[ImportFailure, amino.List[Any]])  # line 125
        def run() -> 'Do':  # line 126
            from amino.list import Lists  # line 127
            exports = yield Either.import_name(modpath, '__all__')  # line 128
            yield Lists.wrap(exports).traverse(lambda a: Either.import_name(modpath, a), Either)  # line 129
        return _coconut_tail_call(run)  # line 130

    @property  # line 132
    @_coconut_tco  # line 132
    def is_right(self) -> 'amino.Boolean':  # line 133
        return _coconut_tail_call(boolean.Boolean, isinstance(self, Right))  # line 134

    @property  # line 136
    @_coconut_tco  # line 136
    def is_left(self) -> 'amino.Boolean':  # line 137
        return _coconut_tail_call(boolean.Boolean, isinstance(self, Left))  # line 138

    @property  # line 140
    @_coconut_tco  # line 140
    def __left_value(self) -> 'A':  # line 141
        return _coconut_tail_call(cast, A, self.value)  # line 142

    @property  # line 144
    @_coconut_tco  # line 144
    def __right_value(self) -> 'B':  # line 145
        return _coconut_tail_call(cast, B, self.value)  # line 146

    def leffect(self, f: '_coconut.typing.Callable[[A], Any]') -> 'Either[A, B]':  # line 148
        if self.is_left:  # line 149
            f(self.__left_value)  # line 150
        return self  # line 151

    def bieffect(self, l: '_coconut.typing.Callable[[A], Any]', r: '_coconut.typing.Callable[[B], Any]') -> 'Either[A, B]':  # line 153
        self.cata(l, r)  # line 154
        return self  # line 155

    def cata(self, fl: '_coconut.typing.Callable[[A], C]', fr: '_coconut.typing.Callable[[B], C]') -> 'C':  # line 157
        return fl(self.__left_value) if self.is_left else fr(self.__right_value)  # line 158

    def bimap(self, fl: '_coconut.typing.Callable[[A], C]', fr: '_coconut.typing.Callable[[B], D]') -> 'Either[C, D]':  # line 160
        return Left(fl(self.__left_value)) if self.is_left else Right(fr(self.__right_value))  # line 161

    @_coconut_tco  # line 163
    def recover_with(self, f: '_coconut.typing.Callable[[A], Either[C, B]]') -> 'Either[C, B]':  # line 163
        return _coconut_tail_call(self.cata, f, Right)  # line 164

    @_coconut_tco  # line 166
    def right_or_map(self, f: '_coconut.typing.Callable[[A], C]') -> 'C':  # line 166
        return _coconut_tail_call(self.cata, f, I)  # line 167

    @_coconut_tco  # line 169
    def value_or(self, f: '_coconut.typing.Callable[[A], B]') -> 'B':  # line 169
        return _coconut_tail_call(self.cata, f, I)  # line 170

    @_coconut_tco  # line 172
    def left_or(self, f: '_coconut.typing.Callable[[B], A]') -> 'A':  # line 172
        return _coconut_tail_call(self.cata, I, f)  # line 173

    @_coconut_tco  # line 175
    def left_or_map(self, f: '_coconut.typing.Callable[[B], A]') -> 'A':  # line 175
        return _coconut_tail_call(self.cata, I, f)  # line 176

    @property  # line 178
    @_coconut_tco  # line 178
    def ljoin(self) -> 'Either[A, C]':  # line 179
        return _coconut_tail_call(self.right_or_map, Left)  # line 180

    @_coconut_tco  # line 182
    def __str__(self) -> 'str':  # line 182
        return _coconut_tail_call('{}({})'.format, self.__class__.__name__, self.value)  # line 183

    @_coconut_tco  # line 185
    def __repr__(self) -> 'str':  # line 185
        return _coconut_tail_call('{}({!r})'.format, self.__class__.__name__, self.value)  # line 186

    @property  # line 188
    def to_list(self) -> 'amino.List[B]':  # line 189
        return self.to_maybe.to_list  # line 190

    def lmap(self, f: '_coconut.typing.Callable[[A], C]') -> 'Either[C, B]':  # line 192
        return cast(Either, Left(f(self.__left_value))) if self.is_left else cast(Either, Right(self.__right_value))  # line 193

    @_coconut_tco  # line 195
    def get_or_raise(self) -> 'B':  # line 195
        def fail(err: 'A') -> 'B':  # line 196
            raise err if isinstance(err, Exception) else Exception(err)  # line 197
        return _coconut_tail_call(self.cata, fail, I)  # line 198

    @property  # line 200
    @_coconut_tco  # line 200
    def fatal(self) -> 'B':  # line 201
        return _coconut_tail_call(self.get_or_raise)  # line 202

    @_coconut_tco  # line 204
    def __iter__(self) -> 'Iterator[B]':  # line 204
        return _coconut_tail_call(iter, self.to_list)  # line 205

    @property  # line 207
    @_coconut_tco  # line 207
    def swap(self) -> 'Either[B, A]':  # line 208
        return _coconut_tail_call(self.cata, Right, Left)  # line 209

    @property  # line 211
    def json_repr(self) -> 'B':  # line 212
        return self.to_maybe.json_repr  # line 213

    @_coconut_tco  # line 215
    def accum_error(self, b: 'Either[A, C]') -> 'Either[A, C]':  # line 215
        return _coconut_tail_call(self.accum_error_f, lambda: b)  # line 216

    @_coconut_tco  # line 218
    def accum_error_f(self, f: '_coconut.typing.Callable[[], Either[A, C]]', *a, **kw) -> 'Either[A, C]':  # line 218
        _coconut_match_to = self  # line 219
        _coconut_match_check = False  # line 219
        if (_coconut.isinstance(_coconut_match_to, Left)) and (_coconut.len(_coconut_match_to) == 1):  # line 219
            value = _coconut_match_to[0]  # line 219
            _coconut_match_check = True  # line 219
        if _coconut_match_check:  # line 219
            _coconut_match_to = f(*a, **kw)  # line 219
            _coconut_match_check = False  # line 219
            if (_coconut.isinstance(_coconut_match_to, Left)) and (_coconut.len(_coconut_match_to) == 1):  # line 219
                err = _coconut_match_to[0]  # line 219
                _coconut_match_check = True  # line 219
            if _coconut_match_check:  # line 219
                monoid = Monoid.fatal_for(value)  # line 223
                return _coconut_tail_call(Left, monoid.combine(value, err))  # line 224
            if not _coconut_match_check:  # line 225
                r = _coconut_match_to  # line 225
                _coconut_match_check = True  # line 225
                if _coconut_match_check:  # line 225
                    return r  # line 226
        if not _coconut_match_check:  # line 227
            r = _coconut_match_to  # line 227
            _coconut_match_check = True  # line 227
            if _coconut_match_check:  # line 227
                return r  # line 228
# def acc(v: A) -> Either[A, C]:
#     monoid = Monoid.fatal_for(self.__left_value)
#     return monoid.combine(self.__left_value, v)
# return f(*a, **kw).lmap(acc) if self.is_left else self

    @_coconut_tco  # line 234
    def accum_error_lift(self, f: '_coconut.typing.Callable[[], Either[A, C]]', *a, **kw) -> 'Either[A, C]':  # line 234
        _coconut_match_to = self  # line 235
        _coconut_match_check = False  # line 235
        if (_coconut.isinstance(_coconut_match_to, Left)) and (_coconut.len(_coconut_match_to) == 1):  # line 235
            value = _coconut_match_to[0]  # line 235
            _coconut_match_check = True  # line 235
        if _coconut_match_check:  # line 235
            _coconut_match_to = f(*a, **kw)  # line 235
            _coconut_match_check = False  # line 235
            if (_coconut.isinstance(_coconut_match_to, Left)) and (_coconut.len(_coconut_match_to) == 1):  # line 235
                err = _coconut_match_to[0]  # line 235
                _coconut_match_check = True  # line 235
            if _coconut_match_check:  # line 235
                monoid = Monoid.fatal_for(value)  # line 239
                monad = Monad.fatal_for(value)  # line 240
                return _coconut_tail_call(Left, monoid.combine(self.__left_value, monad.pure(err)))  # line 241
            if not _coconut_match_check:  # line 242
                r = _coconut_match_to  # line 242
                _coconut_match_check = True  # line 242
                if _coconut_match_check:  # line 242
                    return r  # line 243
        if not _coconut_match_check:  # line 244
            r = _coconut_match_to  # line 244
            _coconut_match_check = True  # line 244
            if _coconut_match_check:  # line 244
                return r  # line 245
# def acc(v: A) -> Either[A, C]:
#     monoid = Monoid.fatal_for(self.__left_value)
#     monad = Monad.fatal_for(self.__left_value)
#     return monoid.combine(self.__left_value, monad.pure(v))
# return f(*a, **kw).lmap(acc) if self.is_left else self

    def filter_with(self, f: '_coconut.typing.Callable[[B], bool]', g: '_coconut.typing.Callable[[B], C]') -> 'Either[C, B]':  # line 252
        return self // (lambda a: Right(a) if f(a) else Left(g(a)))  # line 253

    @_coconut_tco  # line 255
    def left_contains(self, a: 'A') -> 'boolean.Boolean':  # line 255
        return _coconut_tail_call(boolean.Boolean, self.is_left and self.__left_value == a)  # line 256


class Right(_coconut.collections.namedtuple("Right", "value"), Generic[A, B], Either[A, B]):  # line 259
    __slots__ = ()  # line 259
    __ne__ = _coconut.object.__ne__  # line 259
    def __eq__(self, other: 'Any') -> 'bool':  # line 261
        return isinstance(other, Right) and self._Either__right_value == other._Either__right_value  # line 262


class Left(_coconut.collections.namedtuple("Left", "value"), Generic[A, B], Either[A, B]):  # line 265
    __slots__ = ()  # line 265
    __ne__ = _coconut.object.__ne__  # line 265
    def __eq__(self, other: 'Any') -> 'bool':  # line 267
        return isinstance(other, Left) and self._Either__left_value == other._Either__left_value  # line 268


@_coconut_tco  # line 271
def Try(f: '_coconut.typing.Callable[[], A]', *a: 'Any', **kw: 'Any') -> 'Either[Exception, A]':  # line 271
    try:  # line 272
        return Right(f(*a, **kw))  # line 273
    except Exception as e:  # line 274
        return _coconut_tail_call(Left, e)  # line 275


__all__ = ('Either', 'Left', 'Right', 'ImportFailure', 'ImportException', 'InvalidLocator', 'Try')  # line 278
