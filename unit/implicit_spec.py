from typing import Callable

from amino import Just, Map, List
from amino.test import Spec
from amino.instances.maybe import MaybeMonad
from amino.tc.base import (ImplicitInstances, Instances, InstancesMetadata,
                           AutoImplicitInstances, TypeClass)
from amino.tc.monoid import Monoid
from amino.lazy import lazy
from amino.instances.list import ListMonoid
from amino.tc.functor import Functor


class A:

    def __init__(self, a: int) -> None:
        self.a = a


class AMonoid(Monoid):

    @property
    def empty(self) -> A:
        return A(0)

    def combine(self, l: A, r: A) -> A:
        return A(l.a + r.a)


class AInstances(ImplicitInstances):

    @lazy
    def _instances(self) -> Map[str, TypeClass]:
        return Map({Monoid: AMonoid()})


Instances.add(InstancesMetadata('A', 'unit.implicit_spec', 'AInstances'))


class B:
    pass


class BFunctor(Functor):

    def map(self, fa: B, f: Callable) -> B:
        return fa


class BInstances(AutoImplicitInstances):
    tpe = B

    @lazy
    def _instances(self) -> Map[str, TypeClass]:
        return Map({Functor: BFunctor()})


class ImplicitSpec(Spec):

    def set_attr(self) -> None:
        Just(1).map.__wrapped__.__self__.should.be.a(MaybeMonad)

    def manual(self) -> None:
        Monoid[A].should.be.a(AMonoid)
        Monoid[List].should.be.a(ListMonoid)
        Functor[B].should.be.a(BFunctor)

__all__ = ('ImplicitSpec',)
