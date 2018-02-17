import re
import abc
from typing import TypeVar, Generic, Callable

from amino.tc.base import TypeClass
from amino.func import I
from amino import _
from amino.tc.functor import apply_n

A = TypeVar('A')
B = TypeVar('B')


class TraverseF(Generic[A]):
    pass


class TraverseG(Generic[A]):
    pass

F = TraverseF
G = TraverseG

F0 = TypeVar('F0', bound=TraverseF)
G0 = TypeVar('G0', bound=TraverseG)


class Traverse(Generic[F0], TypeClass[F0]):
    traverse_re = re.compile('^traverse(\d+)$')
    # FIXME lens functions return index lenses, which is not a property of Traverse

    @abc.abstractmethod
    def traverse(self, fa: F[G[A]], f: Callable[[A], B], tpe: type) -> G[F[B]]:
        ...

    def traverse_n(self, num: int, fa: F, f: Callable[..., B], tpe: type) -> F:
        return apply_n(self, num, fa, f, self.traverse, tpe)

    def __getattr__(self, name: str) -> Callable:
        match = self.traverse_re.match(name)
        if match is None:
            raise AttributeError(f'''`Traverse` object has no attribute `{name}`''')
        return lambda *a: self.traverse_n(int(match.group(1)), *a)

    def flat_traverse(self, fa: F[G[A]], f: Callable[[A], F[B]], tpe: type) -> G[F[B]]:
        return self.traverse(fa, f, tpe).map(_.join)  # type: ignore

    def sequence(self, fa: F[G[A]], tpe: type) -> G[F[A]]:
        return self.traverse(fa, I, tpe)

    def flat_sequence(self, fa: F[G[A]], tpe: type) -> G[F[B]]:
        return self.sequence(fa, tpe).map(_.join)  # type: ignore

__all__ = ('Traverse',)
