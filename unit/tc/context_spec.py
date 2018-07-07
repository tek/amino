from typing import TypeVar, Callable, Any, Generic

from amino.tc.monad import Monad
from amino import List, ADT
from amino.case import Case
from amino.algebra import Algebra
from amino.test.spec_spec import Spec
from amino.tc.context import context, Bindings

A = TypeVar('A')
B = TypeVar('B')
X = TypeVar('X')
Alg = TypeVar('Alg', bound=Algebra)


@context(A=Monad)
def monad_constraint(a: A, f: Callable[[A], A]) -> A:
    return a.flat_map(f)


@context(**monad_constraint.bounds)
def monad_constraint_wrap(bindings: Bindings, a: A, f: Callable[[A], A]) -> None:
    return monad_constraint(**bindings.bindings)(a, f)


class Al(Generic[A], ADT['Al']):
    pass


class Ala(Al[A]):

    def __init__(self, a: A) -> None:
        self.a = a


@context(A=Monad)
class MonadConstraint(Case, alg=Al):

    def __init__(self, bindings: Bindings, i: int) -> None:
        self.bindings = bindings
        self.i = i

    def ala(self, a: Ala[A], f: Callable[[Any], B]) -> B:
        return monad_constraint(self.bindings)(a.a, f)


target = List(2, 6, 3, 7)


class ContextSpec(Spec):

    def _f(self, a: int) -> List[int]:
        return List(a + 1, a + 5)

    def func(self) -> None:
        r = monad_constraint_wrap(A=List)(List(1, 2), self._f)
        r.should.equal(target)

    def case(self) -> None:
        r = MonadConstraint(A=List)(1)(Ala(List(1, 2)), self._f)
        r.should.equal(target)

    def err(self) -> None:
        MonadConstraint.when.called_with().should.throw(Exception)


__all__ = ('ContextSpec',)
