import abc
from typing import TypeVar, Callable, Any, List

from amino.tc.base import TypeClass, tc_prop
from amino.func import ReplaceVal
from amino.tc.apply_n import ApplyN

F = TypeVar('F')
A = TypeVar('A')
B = TypeVar('B')


class Functor(TypeClass, ApplyN):

    def apply_n_funcs(self) -> List[str]:
        return ['map']

    @abc.abstractmethod
    def map(self, fa: F, f: Callable[[A], B]) -> F:
        ...

    def __truediv__(self, fa, f):
        return self.map(fa, f)

    def replace(self, fa: F, b: B) -> F:
        return self.map(fa, ReplaceVal(b))

    @tc_prop
    def void(self, fa: F) -> F:
        return self.replace(fa, None)

    def foreach(self, fa: F, f: Callable[[A], Any]) -> F:
        def effect(a: A) -> A:
            f(a)
            return a
        return self.map(fa, effect)

    __mod__ = foreach

__all__ = ('Functor',)
