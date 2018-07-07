import abc
from typing import TypeVar, Generic, Callable, List

from amino.tc.base import TypeClass
from amino.func import I
from amino import _
from amino.tc.apply_n import ApplyN

A = TypeVar('A')
B = TypeVar('B')


class TraverseF(Generic[A], abc.ABC):
    pass


class TraverseG(Generic[A], abc.ABC):
    pass

F = TraverseF
G = TraverseG

F0 = TypeVar('F0', bound=TraverseF)
G0 = TypeVar('G0', bound=TraverseG)


class Traverse(TypeClass, ApplyN):
    # FIXME lens functions return index lenses, which is not a property of Traverse

    def apply_n_funcs(self) -> list:
        return ['traverse']

    @abc.abstractmethod
    def traverse(self, fa: F[G[A]], f: Callable[[A], B], tpe: type) -> G[F[B]]:
        ...

    def flat_traverse(self, fa: F[G[A]], f: Callable[[A], F[B]], tpe: type) -> G[F[B]]:
        return self.traverse(fa, f, tpe).map(_.join)  # type: ignore

    def sequence(self, fa: F[G[A]], tpe: type) -> G[F[A]]:
        return self.traverse(fa, I, tpe)

    def flat_sequence(self, fa: F[G[A]], tpe: type) -> G[F[B]]:
        return self.sequence(fa, tpe).map(_.join)  # type: ignore

__all__ = ('Traverse',)
