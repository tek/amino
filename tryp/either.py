from typing import TypeVar, Generic, Callable, Union
from functools import wraps, partial  # type: ignore
from operator import eq, is_not  # type: ignore
from abc import ABCMeta, abstractmethod

from fn import F, _  # type: ignore

A = TypeVar('A')

B = TypeVar('B')


class Either(Generic[A, B], metaclass=ABCMeta):

    def __init__(self):
        self.value = None  # type: Union[A, B, None]


class Left(Either):

    def __init__(self, value: A) -> None:
        self.value = value


class Right(Either):

    def __init__(self, value: B) -> None:
        self.value = value

__all__ = ['Either']
