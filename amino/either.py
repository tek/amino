import importlib
from typing import TypeVar, Generic, Callable, Union, Any
from typing import Tuple  # NOQA

from amino import boolean
from amino.func import I
from amino.tc.base import Implicits

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class Either(Generic[A, B], Implicits, implicits=True):

    def __init__(self, value: Union[A, B]) -> None:
        self.value = value

    @staticmethod
    def import_name(modname, name):
        try:
            mod = importlib.import_module(modname)
        except ImportError as e:
            return Left(e)
        else:
            if hasattr(mod, name):
                return Right(getattr(mod, name))
            else:
                return Left('{} has no attribute {}'.format(mod, name))

    @staticmethod
    def import_path(path):
        from amino.list import List
        return (
            List.wrap(path.rsplit('.', 1))
            .lift_all(0, 1)
            .to_either('invalid module path: {}'.format(path))
            .flat_map2(Either.import_name)
        )

    @staticmethod
    def import_module(modname):
        try:
            mod = importlib.import_module(modname)
        except ImportError as e:
            return Left(e)
        else:
            return Right(mod)

    @property
    def is_right(self):
        return boolean.Boolean(isinstance(self, Right))

    @property
    def is_left(self):
        return boolean.Boolean(isinstance(self, Left))

    def leffect(self, f):
        if self.is_left:
            f(self.value)
        return self

    def cata(self, fl: Callable[[A], Any], fr: Callable[[B], Any]):
        f = fl if self.is_left else fr
        return f(self.value)  # type: ignore

    def recover_with(self, f: Callable[[A], 'Either[A, B]']):
        return self.cata(f, Right)

    def right_or_map(self, f: Callable[[A], Any]):
        return self.cata(f, I)

    def left_or_map(self, f: Callable[[B], Any]):
        return self.cata(I, f)

    @property
    def ljoin(self):
        return self.right_or_map(Left)

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, self.value)

    @property
    def to_list(self):
        return self.to_maybe.to_list

    def lmap(self, f: Callable[[A], Any]):
        return Left(f(self.value)) if self.is_left else self  # type: ignore

    def zip(self, other: 'Either[Any, C]') -> 'Either[A, Tuple[B, C]]':
        if self.is_right and other.is_right:
            return Right((self.value, other.value))
        elif self.is_left:
            return self
        else:
            return other

    @property
    def get_or_raise(self):
        def fail(err):
            raise err if isinstance(err, Exception) else Exception(err)
        return self.cata(fail, I)

    def __iter__(self):
        return iter(self.to_list)

    @property
    def swap(self):
        return Left(self.value) if self.is_right else Right(self.value)


class Right(Either):

    def __eq__(self, other):
        return isinstance(other, Right) and self.value == other.value


class Left(Either):

    def __eq__(self, other):
        return isinstance(other, Left) and self.value == other.value

__all__ = ('Either', 'Left', 'Right')
