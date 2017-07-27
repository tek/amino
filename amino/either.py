import importlib
from typing import TypeVar, Generic, Callable, Union, Any, cast, Iterator

import amino  # noqa
from amino import boolean
from amino.func import I
from amino.tc.base import Implicits
from amino.util.mod import unsafe_import_name

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class Either(Generic[A, B], Implicits, implicits=True):

    def __init__(self, value: Union[A, B]) -> None:
        self.value = value

    @staticmethod
    def import_name(mod: str, name: str) -> Any:
        try:
            value = unsafe_import_name(mod, name)
        except ImportError as e:
            return Left(e)
        else:
            return Left('{} has no attribute {}'.format(mod, name)) if value is None else Right(value)

    @staticmethod
    def import_path(path: str) -> Any:
        from amino.list import List
        return (
            List.wrap(path.rsplit('.', 1))
            .lift_all(0, 1)
            .to_either('invalid module path: {}'.format(path))
            .flat_map2(Either.import_name)
        )

    @staticmethod
    def import_module(modname: str) -> Any:
        try:
            mod = importlib.import_module(modname)
        except ImportError as e:
            return Left(e)
        else:
            return Right(mod)

    @property
    def is_right(self) -> 'amino.Boolean':
        return boolean.Boolean(isinstance(self, Right))

    @property
    def is_left(self) -> 'amino.Boolean':
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

    def bieffect(self, l: Callable[[A], Any],
                 r: Callable[[B], Any]) -> 'Either[A, B]':
        self.cata(l, r)
        return self

    def cata(self, fl: Callable[[A], C], fr: Callable[[B], C]) -> C:
        return fl(self.__left_value) if self.is_left else fr(self.__right_value)

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
    def to_list(self) -> 'amino.List[B]':
        return self.to_maybe.to_list

    def lmap(self, f: Callable[[A], C]) -> 'Either[C, B]':
        return cast(Either, Left(f(self.__left_value))) if self.is_left else cast(Either, Right(self.__right_value))

    @property
    def get_or_raise(self) -> B:
        def fail(err: A) -> B:
            raise err if isinstance(err, Exception) else Exception(err)
        return self.cata(fail, I)

    @property
    def fatal(self) -> B:
        return self.get_or_raise

    def __iter__(self) -> Iterator[B]:
        return iter(self.to_list)

    @property
    def swap(self) -> 'Either[B, A]':
        return self.cata(Right, Left)

    @property
    def json(self) -> B:
        return self.to_maybe.json


class Right(Either):

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Right) and self._Either__right_value == other._Either__right_value


class Left(Either):

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Left) and self._Either__left_value == other._Either__left_value

__all__ = ('Either', 'Left', 'Right')
