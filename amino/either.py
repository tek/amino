import abc
import importlib
from typing import TypeVar, Generic, Union, Any, cast, Iterator, Type, Callable
from types import ModuleType
from pathlib import Path

import amino
from amino import boolean
from amino.func import I
from amino.tc.base import F
from amino.util.mod import unsafe_import_name
from amino.tc.monoid import Monoid
from amino.tc.monad import Monad
from amino.util.string import ToStr
from amino.do import do, Do
from amino.util.exception import format_exception

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')
D = TypeVar('D')
E = TypeVar('E', bound=Exception)


class ImportFailure(ToStr):

    @abc.abstractproperty
    def expand(self) -> 'amino.list.List[str]':
        ...


class ImportException(ImportFailure):

    def __init__(self, desc: str, exc: Exception) -> None:
        self.desc = desc
        self.exc = exc

    def _arg_desc(self) -> 'amino.list.List':
        return amino.List(self.desc, str(self.exc))

    @property
    def expand(self) -> 'amino.list.List':
        return format_exception(self.exc).cons(self.desc)


class InvalidLocator(ImportFailure):

    def __init__(self, msg: str) -> None:
        self.msg = msg

    def _arg_desc(self) -> 'amino.list.List':
        return amino.List(self.msg)

    @property
    def expand(self) -> 'amino.list.List':
        return amino.List(self.msg)


class Either(Generic[A, B], F[B], implicits=True):

    @staticmethod
    def import_name(mod: str, name: str) -> 'Either[ImportFailure, B]':
        try:
            value = (
                __builtins__[name]
                if mod == '__builtins__' else
                unsafe_import_name(mod, name)
            )
        except Exception as e:
            return Left(ImportException(f'{mod}.{name}', e))
        else:
            return Left(InvalidLocator(f'{mod} has no attribute {name}')) if value is None else Right(value)

    @staticmethod
    def import_path(path: str) -> 'Either[ImportFailure, B]':
        from amino.list import List
        return (
            List.wrap(path.rsplit('.', 1))
            .lift_all(0, 1)
            .to_either(InvalidLocator(f'invalid module path: {path}'))
            .flat_map2(lambda a, b: Either.import_name(a, b).lmap(lambda c: ImportException(path, c)))
        )

    @staticmethod
    def import_module(modname: str) -> 'Either[ImportFailure, ModuleType]':
        try:
            mod = importlib.import_module(modname)
        except Exception as e:
            return Left(ImportException(modname, e))
        else:
            return Right(mod)

    @staticmethod
    def import_file(path: Path) -> 'Either[ImportFailure, ModuleType]':
        from amino.maybe import Maybe
        def step2(spec: importlib._bootstrap.ModuleSpec) -> ModuleType:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        try:
            module = Maybe.check(importlib.util.spec_from_file_location('temp', str(path))) / step2
        except Exception as e:
            return Left(ImportException(str(path), e))
        else:
            return module.to_either(InvalidLocator(f'failed to import `{path}`'))

    @staticmethod
    def import_from_file(path: Path, name: str) -> 'Either[ImportFailure, B]':
        @do(Either[ImportFailure, B])
        def run() -> Do:
            module = yield Either.import_file(path)
            attr = getattr(module, name, None)
            yield (
                Left(InvalidLocator(f'{path} has no attribute {name}'))
                if attr is None else
                Right(attr)
            )
        return run()

    @staticmethod
    def exports(modpath: str) -> 'Either[ImportFailure, amino.List[Any]]':
        @do(Either[ImportFailure, amino.List[Any]])
        def run() -> Do:
            from amino.list import Lists
            exports = yield Either.import_name(modpath, '__all__')
            yield Lists.wrap(exports).traverse(lambda a: Either.import_name(modpath, a), Either)
        return run()

    @staticmethod
    def getattr(obj: Any, attr: str) -> 'Either[str, A]':
        return Right(getattr(obj, attr)) if hasattr(obj, attr) else Left(f'`{obj}` has no attribute `{attr}`')

    @property
    def is_right(self) -> 'amino.boolean.Boolean':
        return boolean.Boolean(isinstance(self, Right))

    @property
    def is_left(self) -> 'amino.boolean.Boolean':
        return boolean.Boolean(isinstance(self, Left))

    @property
    def __left_value(self) -> A:
        return cast(A, self.value)

    @property
    def __right_value(self) -> B:
        return cast(B, self.value)

    def leffect(self, f: Callable[[A], Any]) -> 'Either[A, B]':
        if self.is_left:
            f(self.__left_value)
        return self

    def bieffect(self, l: Callable[[A], Any], r: Callable[[B], Any]) -> 'Either[A, B]':
        self.cata(l, r)
        return self

    def cata(self, fl: Callable[[A], C], fr: Callable[[B], C]) -> C:
        return fl(self.__left_value) if self.is_left else fr(self.__right_value)

    def bimap(self, fl: Callable[[A], C], fr: Callable[[B], D]) -> 'Either[C, D]':
        return Left(fl(self.__left_value)) if self.is_left else Right(fr(self.__right_value))

    def recover_with(self, f: Callable[[A], 'Either[C, B]']) -> 'Either[C, B]':
        return self.cata(f, Right)

    def right_or_map(self, f: Callable[[A], C]) -> C:
        return self.cata(f, I)

    def value_or(self, f: Callable[[A], B]) -> B:
        return self.cata(f, I)

    def left_or(self, f: Callable[[B], A]) -> A:
        return self.cata(I, f)

    def left_or_map(self, f: Callable[[B], A]) -> A:
        return self.cata(I, f)

    @property
    def ljoin(self) -> 'Either[A, C]':
        return self.right_or_map(Left)

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self.value)

    def __repr__(self) -> str:
        return '{}({!r})'.format(self.__class__.__name__, self.value)

    @property
    def to_list(self) -> 'amino.list.List[B]':
        return self.to_maybe.to_list

    def lmap(self, f: Callable[[A], C]) -> 'Either[C, B]':
        return cast(Either, Left(f(self.__left_value))) if self.is_left else cast(Either, Right(self.__right_value))

    def get_or_raise(self) -> B:
        def fail(err: A) -> B:
            raise err if isinstance(err, Exception) else Exception(err)
        return self.cata(fail, I)

    @property
    def fatal(self) -> B:
        return self.get_or_raise()

    def __iter__(self) -> Iterator[B]:
        return iter(self.to_list)

    @property
    def swap(self) -> 'Either[B, A]':
        return self.cata(Right, Left)

    @property
    def json_repr(self) -> B:
        return self.to_maybe.json_repr

    def accum_error(self, b: 'Either[A, C]') -> 'Either[A, C]':
        return self.accum_error_f(lambda: b)

    def accum_error_f(self, f: Callable[[], 'Either[A, C]'], *a, **kw) -> 'Either[A, C]':
        def acc(v: A) -> 'Either[A, C]':
            monoid = Monoid.fatal_for(self.__left_value)
            return monoid.combine(self.__left_value, v)
        return f(*a, **kw).lmap(acc) if self.is_left else self

    def accum_error_lift(self, f: Callable[[], 'Either[A, C]'], *a, **kw) -> 'Either[A, C]':
        def acc(v: A) -> 'Either[A, C]':
            monoid = Monoid.fatal_for(self.__left_value)
            monad = Monad.fatal_for(self.__left_value)
            return monoid.combine(self.__left_value, monad.pure(v))
        return f(*a, **kw).lmap(acc) if self.is_left else self

    def filter_with(self, f: Callable[[B], bool], g: Callable[[B], C]) -> 'Either[C, B]':
        return self // (lambda a: Right(a) if f(a) else Left(g(a)))

    def left_contains(self, a: A) -> 'amino.boolean.Boolean':
        return boolean.Boolean(self.is_left and self.__left_value == a)


class Right(Either[A, B]):

    def __init__(self, value: B) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Right) and self._Either__right_value == other._Either__right_value


class Left(Either[A, B]):

    def __init__(self, value: A) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Left) and self._Either__left_value == other._Either__left_value


def Try(f: Callable[..., A], *a: Any, **kw: Any) -> Either[Exception, A]:
    try:
        return Right(f(*a, **kw))
    except Exception as e:
        return Left(e)


__all__ = ('Either', 'Left', 'Right', 'ImportFailure', 'ImportException', 'InvalidLocator', 'Try')
