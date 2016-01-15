import abc
from typing import Generic, Callable, Any, TypeVar

A = TypeVar('A')


class Transformer(Generic[A], metaclass=abc.ABCMeta):

    def __init__(self, val: A) -> None:
        self.val = val

    @abc.abstractmethod
    def flat_map(self, f: Callable[[A], Any]) -> 'Transformer':
        ...

    def __floordiv__(self, f):
        return self.flat_map(f)

    def effect(self, f: Callable[[A], Any]):
        f(self.val)
        return self

    def __matmul__(self, f):
        return self.effect(f)

    def effect0(self, f: Callable[[], Any]):
        f()
        return self

    def __mod__(self, f):
        return self.effect0(f)

__all__ = ('Transformer')
