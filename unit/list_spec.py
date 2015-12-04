import sure  # NOQA
from flexmock import flexmock  # NOQA

from fn import _

from tek import Spec  # type: ignore

from tryp import List, Empty, Just


class List_(Spec, ):

    def setup(self, *a, **kw):
        super(List_, self).setup(*a, **kw)

    def map(self):
        List(1, 2, 3) \
            .map(_ + 1) \
            .should.equal(List(2, 3, 4))

    def flatMap(self):
        List(1, 2, 3) \
            .flatMap(lambda v: [v, v + 1]) \
            .should.equal(List(1, 2, 2, 3, 3, 4))

    def flattenMaybes(self):
        List(Just(4), Empty(), Just(5), Empty()) \
            .flatMap(_.toList) \
            .should.equal(List(4, 5))

    def flatMapMaybe(self):
        List(1, 2, 3)\
            .flatMap(lambda a: Empty() if a % 2 == 0 else Just(a + 1))\
            .should.equal(List(2, 4))

    def find(self):
        l = List(1, 6, 9)
        l.find(_ % 2 == 0).should.equal(Just(6))
        l.find(_ == 3).should.equal(Empty())

__all__ = ['List_']
