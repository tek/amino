#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xc65d39be

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

import abc
import importlib
from typing import TypeVar
from typing import Generic
from typing import Union
from typing import Any
from typing import cast
from typing import Iterator
from typing import Type
from typing import Generator
from types import ModuleType
from pathlib import Path

import amino
from amino import boolean
from amino.func import I
from amino.tc.base import F
from amino.util.mod import unsafe_import_name
from amino.tc.monoid import Monoid
from amino.util.string import ToStr
from amino.do import do
from amino.util.exception import format_exception

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
D = TypeVar('D')
E = TypeVar('E', bound=Exception)


class ImportFailure(ToStr):

    @abc.abstractproperty
    def expand(self) -> 'amino.List[str]':
        ...


class ImportException(ImportFailure):

    def __init__(self, desc: 'str', exc: 'Exception') -> 'None':
        self.desc = desc
        self.exc = exc

    @_coconut_tco
    def _arg_desc(self) -> 'amino.List[str]':
        return _coconut_tail_call(amino.List, self.desc, str(self.exc))

    @property
    @_coconut_tco
    def expand(self) -> 'amino.List[str]':
        return _coconut_tail_call(format_exception(self.exc).cons, self.desc)


class InvalidLocator(ImportFailure):

    def __init__(self, msg: 'str') -> 'None':
        self.msg = msg

    @_coconut_tco
    def _arg_desc(self) -> 'amino.List[str]':
        return _coconut_tail_call(amino.List, self.msg)

    @property
    @_coconut_tco
    def expand(self) -> 'amino.List[str]':
        return _coconut_tail_call(amino.List, self.msg)


class Either(Generic[A, B], F[B], implicits=True):

    @staticmethod
    @_coconut_tco
    def import_name(mod: 'str', name: 'str') -> 'Either[ImportFailure, B]':
        try:
            value = unsafe_import_name(mod, name)
        except Exception as e:
            return _coconut_tail_call(Left, ImportException(f'{mod}.{name}', e))
        else:
            return Left(InvalidLocator(f'{mod} has no attribute {name}')) if value is None else Right(value)

    @staticmethod
    def import_path(path: 'str') -> 'Either[ImportFailure, B]':
        from amino.list import List
        return (List.wrap(path.rsplit('.', 1)).lift_all(0, 1).to_either(InvalidLocator(f'invalid module path: {path}')).flat_map2(lambda a, b: Either.import_name(a, b).lmap(lambda c: ImportException(path, c))))

    @staticmethod
    @_coconut_tco
    def import_module(modname: 'str') -> 'Either[ImportFailure, ModuleType]':
        try:
            mod = importlib.import_module(modname)
        except Exception as e:
            return _coconut_tail_call(Left, ImportException(modname, e))
        else:
            return _coconut_tail_call(Right, mod)

    @staticmethod
    @_coconut_tco
    def import_file(path: 'Path') -> 'Either[ImportFailure, ModuleType]':
        from amino.maybe import Maybe
        def step2(spec: 'importlib._bootstrap.ModuleSpec') -> 'ModuleType':
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        try:
            module = Maybe.check(importlib.util.spec_from_file_location('temp', str(path))) / step2
        except Exception as e:
            return _coconut_tail_call(Left, ImportException(str(path), e))
        else:
            return _coconut_tail_call(module.to_either, InvalidLocator(f'failed to import `{path}`'))

    @staticmethod
    @do('Either[ImportFailure, B]')
    def import_from_file(path: 'Path', name: 'str') -> 'Generator':
        module = yield Either.import_file(path)
        attr = getattr(module, name, None)
        yield (Left(InvalidLocator(f'{path} has no attribute {name}')) if attr is None else Right(attr))

    @staticmethod
    @_coconut_tco
    def catch(f: '_coconut.typing.Callable[[], B]', exc: 'Type[E]') -> 'Either[E, B]':
        try:
            return Right(f())
        except exc as e:
            return _coconut_tail_call(Left, e)

    @staticmethod
    @do('Either[ImportFailure, amino.List[Any]]')
    def exports(modpath: 'str') -> 'Generator':
        from amino.list import Lists
        exports = yield Either.import_name(modpath, '__all__')
        yield Lists.wrap(exports).traverse(lambda a: Either.import_name(modpath, a), Either)

    @property
    @_coconut_tco
    def is_right(self) -> 'amino.Boolean':
        return _coconut_tail_call(boolean.Boolean, isinstance(self, Right))

    @property
    @_coconut_tco
    def is_left(self) -> 'amino.Boolean':
        return _coconut_tail_call(boolean.Boolean, isinstance(self, Left))

    @property
    @_coconut_tco
    def __left_value(self) -> 'A':
        return _coconut_tail_call(cast, A, self.value)

    @property
    @_coconut_tco
    def __right_value(self) -> 'B':
        return _coconut_tail_call(cast, B, self.value)

    def leffect(self, f: '_coconut.typing.Callable[[A], Any]') -> 'Either[A, B]':
        if self.is_left:
            f(self.__left_value)
        return self

    def bieffect(self, l: '_coconut.typing.Callable[[A], Any]', r: '_coconut.typing.Callable[[B], Any]') -> 'Either[A, B]':
        self.cata(l, r)
        return self

    def cata(self, fl: '_coconut.typing.Callable[[A], C]', fr: '_coconut.typing.Callable[[B], C]') -> 'C':
        return fl(self.__left_value) if self.is_left else fr(self.__right_value)

    def bimap(self, fl: '_coconut.typing.Callable[[A], C]', fr: '_coconut.typing.Callable[[B], D]') -> 'Either[C, D]':
        return Left(fl(self.__left_value)) if self.is_left else Right(fr(self.__right_value))

    @_coconut_tco
    def recover_with(self, f: '_coconut.typing.Callable[[A], Either[C, B]]') -> 'Either[C, B]':
        return _coconut_tail_call(self.cata, f, Right)

    @_coconut_tco
    def right_or_map(self, f: '_coconut.typing.Callable[[A], C]') -> 'C':
        return _coconut_tail_call(self.cata, f, I)

    @_coconut_tco
    def value_or(self, f: '_coconut.typing.Callable[[A], B]') -> 'B':
        return _coconut_tail_call(self.cata, f, I)

    @_coconut_tco
    def left_or(self, f: '_coconut.typing.Callable[[B], A]') -> 'A':
        return _coconut_tail_call(self.cata, I, f)

    @_coconut_tco
    def left_or_map(self, f: '_coconut.typing.Callable[[B], A]') -> 'A':
        return _coconut_tail_call(self.cata, I, f)

    @property
    @_coconut_tco
    def ljoin(self) -> 'Either[A, C]':
        return _coconut_tail_call(self.right_or_map, Left)

    @_coconut_tco
    def __str__(self) -> 'str':
        return _coconut_tail_call('{}({})'.format, self.__class__.__name__, self.value)

    @_coconut_tco
    def __repr__(self) -> 'str':
        return _coconut_tail_call('{}({!r})'.format, self.__class__.__name__, self.value)

    @property
    def to_list(self) -> 'amino.List[B]':
        return self.to_maybe.to_list

    def lmap(self, f: '_coconut.typing.Callable[[A], C]') -> 'Either[C, B]':
        return cast(Either, Left(f(self.__left_value))) if self.is_left else cast(Either, Right(self.__right_value))

    @_coconut_tco
    def get_or_raise(self) -> 'B':
        def fail(err: 'A') -> 'B':
            raise err if isinstance(err, Exception) else Exception(err)
        return _coconut_tail_call(self.cata, fail, I)

    @property
    def fatal(self) -> 'B':
        return self.get_or_raise

    @_coconut_tco
    def __iter__(self) -> 'Iterator[B]':
        return _coconut_tail_call(iter, self.to_list)

    @property
    @_coconut_tco
    def swap(self) -> 'Either[B, A]':
        return _coconut_tail_call(self.cata, Right, Left)

    @property
    def json_repr(self) -> 'B':
        return self.to_maybe.json_repr

    @_coconut_tco
    def accum_error(self, b: 'Either[A, C]') -> 'Either[A, C]':
        return _coconut_tail_call(self.accum_error_f, lambda: b)

    def accum_error_f(self, f: '_coconut.typing.Callable[[], Either[A, C]]') -> 'Either[A, C]':
        @_coconut_tco
        def acc(v: 'A') -> 'None':
            return _coconut_tail_call(Monoid.fatal(type(v)).combine, self.__left_value, v)
        return f().lmap(acc) if self.is_left else self

    def filter_with(self, f: '_coconut.typing.Callable[[B], bool]', g: '_coconut.typing.Callable[[B], C]') -> 'Either[C, B]':
        return self // (lambda a: Right(a) if f(a) else Left(g(a)))

    @_coconut_tco
    def left_contains(self, a: 'A') -> 'boolean.Boolean':
        return _coconut_tail_call(boolean.Boolean, self.is_left and self.__left_value == a)


class Right(_coconut.collections.namedtuple("Right", "value"), Generic[A, B], Either[A, B]):
    __slots__ = ()
    __ne__ = _coconut.object.__ne__
    def __eq__(self, other: 'Any') -> 'bool':
        return isinstance(other, Right) and self._Either__right_value == other._Either__right_value


class Left(_coconut.collections.namedtuple("Left", "value"), Generic[A, B], Either[A, B]):
    __slots__ = ()
    __ne__ = _coconut.object.__ne__
    def __eq__(self, other: 'Any') -> 'bool':
        return isinstance(other, Left) and self._Either__left_value == other._Either__left_value

__all__ = ('Either', 'Left', 'Right', 'ImportFailure', 'ImportException', 'InvalidLocator')
