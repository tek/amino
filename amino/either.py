#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0x11958c37

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
from amino.util.string import ToStr  # line 13
from amino.do import do  # line 14
from amino.util.exception import format_exception  # line 15

A = TypeVar('A')  # line 17
B = TypeVar('B')  # line 18
C = TypeVar('C')  # line 19
D = TypeVar('D')  # line 20
E = TypeVar('E', bound=Exception)  # line 21


class ImportFailure(ToStr):  # line 24

    @abc.abstractproperty  # line 26
    def expand(self) -> 'amino.List[str]':  # line 27
        ...  # line 28


class ImportException(ImportFailure):  # line 31

    def __init__(self, desc: 'str', exc: 'Exception') -> 'None':  # line 33
        self.desc = desc  # line 34
        self.exc = exc  # line 35

    @_coconut_tco  # line 37
    def _arg_desc(self) -> 'amino.List[str]':  # line 37
        return _coconut_tail_call(amino.List, self.desc, str(self.exc))  # line 38

    @property  # line 40
    @_coconut_tco  # line 40
    def expand(self) -> 'amino.List[str]':  # line 41
        return _coconut_tail_call(format_exception(self.exc).cons, self.desc)  # line 42


class InvalidLocator(ImportFailure):  # line 45

    def __init__(self, msg: 'str') -> 'None':  # line 47
        self.msg = msg  # line 48

    @_coconut_tco  # line 50
    def _arg_desc(self) -> 'amino.List[str]':  # line 50
        return _coconut_tail_call(amino.List, self.msg)  # line 51

    @property  # line 53
    @_coconut_tco  # line 53
    def expand(self) -> 'amino.List[str]':  # line 54
        return _coconut_tail_call(amino.List, self.msg)  # line 55


class Either(Generic[A, B], F[B], implicits=True):  # line 58

    @staticmethod  # line 60
    @_coconut_tco  # line 60
    def import_name(mod: 'str', name: 'str') -> 'Either[ImportFailure, B]':  # line 61
        try:  # line 62
            value = unsafe_import_name(mod, name)  # line 63
        except Exception as e:  # line 64
            return _coconut_tail_call(Left, ImportException(f'{mod}.{name}', e))  # line 65
        else:  # line 66
            return Left(InvalidLocator(f'{mod} has no attribute {name}')) if value is None else Right(value)  # line 67

    @staticmethod  # line 69
    def import_path(path: 'str') -> 'Either[ImportFailure, B]':  # line 70
        from amino.list import List  # line 71
        return (List.wrap(path.rsplit('.', 1)).lift_all(0, 1).to_either(InvalidLocator(f'invalid module path: {path}')).flat_map2(lambda a, b: Either.import_name(a, b).lmap(lambda c: ImportException(path, c))))  # line 72

    @staticmethod  # line 79
    @_coconut_tco  # line 79
    def import_module(modname: 'str') -> 'Either[ImportFailure, ModuleType]':  # line 80
        try:  # line 81
            mod = importlib.import_module(modname)  # line 82
        except Exception as e:  # line 83
            return _coconut_tail_call(Left, ImportException(modname, e))  # line 84
        else:  # line 85
            return _coconut_tail_call(Right, mod)  # line 86

    @staticmethod  # line 88
    @_coconut_tco  # line 88
    def import_file(path: 'Path') -> 'Either[ImportFailure, ModuleType]':  # line 89
        from amino.maybe import Maybe  # line 90
        def step2(spec: 'importlib._bootstrap.ModuleSpec') -> 'ModuleType':  # line 91
            module = importlib.util.module_from_spec(spec)  # line 92
            spec.loader.exec_module(module)  # line 93
            return module  # line 94
        try:  # line 95
            module = Maybe.check(importlib.util.spec_from_file_location('temp', str(path))) / step2  # line 96
        except Exception as e:  # line 97
            return _coconut_tail_call(Left, ImportException(str(path), e))  # line 98
        else:  # line 99
            return _coconut_tail_call(module.to_either, InvalidLocator(f'failed to import `{path}`'))  # line 100

    @staticmethod  # line 102
    @do('Either[ImportFailure, B]')  # line 102
    def import_from_file(path: 'Path', name: 'str') -> 'Generator':  # line 104
        module = yield Either.import_file(path)  # line 105
        attr = getattr(module, name, None)  # line 106
        yield (Left(InvalidLocator(f'{path} has no attribute {name}')) if attr is None else Right(attr))  # line 107

    @staticmethod  # line 113
    @_coconut_tco  # line 113
    def catch(f: '_coconut.typing.Callable[[], B]', exc: 'Type[E]') -> 'Either[E, B]':  # line 114
        try:  # line 115
            return Right(f())  # line 116
        except exc as e:  # line 117
            return _coconut_tail_call(Left, e)  # line 118

    @staticmethod  # line 120
    @do('Either[ImportFailure, amino.List[Any]]')  # line 120
    def exports(modpath: 'str') -> 'Generator':  # line 122
        from amino.list import Lists  # line 123
        exports = yield Either.import_name(modpath, '__all__')  # line 124
        yield Lists.wrap(exports).traverse(lambda a: Either.import_name(modpath, a), Either)  # line 125

    @property  # line 127
    @_coconut_tco  # line 127
    def is_right(self) -> 'amino.Boolean':  # line 128
        return _coconut_tail_call(boolean.Boolean, isinstance(self, Right))  # line 129

    @property  # line 131
    @_coconut_tco  # line 131
    def is_left(self) -> 'amino.Boolean':  # line 132
        return _coconut_tail_call(boolean.Boolean, isinstance(self, Left))  # line 133

    @property  # line 135
    @_coconut_tco  # line 135
    def __left_value(self) -> 'A':  # line 136
        return _coconut_tail_call(cast, A, self.value)  # line 137

    @property  # line 139
    @_coconut_tco  # line 139
    def __right_value(self) -> 'B':  # line 140
        return _coconut_tail_call(cast, B, self.value)  # line 141

    def leffect(self, f: '_coconut.typing.Callable[[A], Any]') -> 'Either[A, B]':  # line 143
        if self.is_left:  # line 144
            f(self.__left_value)  # line 145
        return self  # line 146

    def bieffect(self, l: '_coconut.typing.Callable[[A], Any]', r: '_coconut.typing.Callable[[B], Any]') -> 'Either[A, B]':  # line 148
        self.cata(l, r)  # line 149
        return self  # line 150

    def cata(self, fl: '_coconut.typing.Callable[[A], C]', fr: '_coconut.typing.Callable[[B], C]') -> 'C':  # line 152
        return fl(self.__left_value) if self.is_left else fr(self.__right_value)  # line 153

    def bimap(self, fl: '_coconut.typing.Callable[[A], C]', fr: '_coconut.typing.Callable[[B], D]') -> 'Either[C, D]':  # line 155
        return Left(fl(self.__left_value)) if self.is_left else Right(fr(self.__right_value))  # line 156

    @_coconut_tco  # line 158
    def recover_with(self, f: '_coconut.typing.Callable[[A], Either[C, B]]') -> 'Either[C, B]':  # line 158
        return _coconut_tail_call(self.cata, f, Right)  # line 159

    @_coconut_tco  # line 161
    def right_or_map(self, f: '_coconut.typing.Callable[[A], C]') -> 'C':  # line 161
        return _coconut_tail_call(self.cata, f, I)  # line 162

    @_coconut_tco  # line 164
    def value_or(self, f: '_coconut.typing.Callable[[A], B]') -> 'B':  # line 164
        return _coconut_tail_call(self.cata, f, I)  # line 165

    @_coconut_tco  # line 167
    def left_or(self, f: '_coconut.typing.Callable[[B], A]') -> 'A':  # line 167
        return _coconut_tail_call(self.cata, I, f)  # line 168

    @_coconut_tco  # line 170
    def left_or_map(self, f: '_coconut.typing.Callable[[B], A]') -> 'A':  # line 170
        return _coconut_tail_call(self.cata, I, f)  # line 171

    @property  # line 173
    @_coconut_tco  # line 173
    def ljoin(self) -> 'Either[A, C]':  # line 174
        return _coconut_tail_call(self.right_or_map, Left)  # line 175

    @_coconut_tco  # line 177
    def __str__(self) -> 'str':  # line 177
        return _coconut_tail_call('{}({})'.format, self.__class__.__name__, self.value)  # line 178

    @_coconut_tco  # line 180
    def __repr__(self) -> 'str':  # line 180
        return _coconut_tail_call('{}({!r})'.format, self.__class__.__name__, self.value)  # line 181

    @property  # line 183
    def to_list(self) -> 'amino.List[B]':  # line 184
        return self.to_maybe.to_list  # line 185

    def lmap(self, f: '_coconut.typing.Callable[[A], C]') -> 'Either[C, B]':  # line 187
        return cast(Either, Left(f(self.__left_value))) if self.is_left else cast(Either, Right(self.__right_value))  # line 188

    @_coconut_tco  # line 190
    def get_or_raise(self) -> 'B':  # line 190
        def fail(err: 'A') -> 'B':  # line 191
            raise err if isinstance(err, Exception) else Exception(err)  # line 192
        return _coconut_tail_call(self.cata, fail, I)  # line 193

    @property  # line 195
    def fatal(self) -> 'B':  # line 196
        return self.get_or_raise  # line 197

    @_coconut_tco  # line 199
    def __iter__(self) -> 'Iterator[B]':  # line 199
        return _coconut_tail_call(iter, self.to_list)  # line 200

    @property  # line 202
    @_coconut_tco  # line 202
    def swap(self) -> 'Either[B, A]':  # line 203
        return _coconut_tail_call(self.cata, Right, Left)  # line 204

    @property  # line 206
    def json_repr(self) -> 'B':  # line 207
        return self.to_maybe.json_repr  # line 208

    @_coconut_tco  # line 210
    def accum_error(self, b: 'Either[A, C]') -> 'Either[A, C]':  # line 210
        return _coconut_tail_call(self.accum_error_f, lambda: b)  # line 211

    def accum_error_f(self, f: '_coconut.typing.Callable[[], Either[A, C]]') -> 'Either[A, C]':  # line 213
        @_coconut_tco  # line 214
        def acc(v: 'A') -> 'None':  # line 214
            return _coconut_tail_call(Monoid.fatal(type(v)).combine, self.__left_value, v)  # line 215
        return f().lmap(acc) if self.is_left else self  # line 216

    def filter_with(self, f: '_coconut.typing.Callable[[B], bool]', g: '_coconut.typing.Callable[[B], C]') -> 'Either[C, B]':  # line 218
        return self // (lambda a: Right(a) if f(a) else Left(g(a)))  # line 219

    @_coconut_tco  # line 221
    def left_contains(self, a: 'A') -> 'boolean.Boolean':  # line 221
        return _coconut_tail_call(boolean.Boolean, self.is_left and self.__left_value == a)  # line 222


class Right(_coconut.collections.namedtuple("Right", "value"), Generic[A, B], Either[A, B]):  # line 225
    __slots__ = ()  # line 225
    __ne__ = _coconut.object.__ne__  # line 225
    def __eq__(self, other: 'Any') -> 'bool':  # line 227
        return isinstance(other, Right) and self._Either__right_value == other._Either__right_value  # line 228


class Left(_coconut.collections.namedtuple("Left", "value"), Generic[A, B], Either[A, B]):  # line 231
    __slots__ = ()  # line 231
    __ne__ = _coconut.object.__ne__  # line 231
    def __eq__(self, other: 'Any') -> 'bool':  # line 233
        return isinstance(other, Left) and self._Either__left_value == other._Either__left_value  # line 234

__all__ = ('Either', 'Left', 'Right', 'ImportFailure', 'ImportException', 'InvalidLocator')  # line 236
