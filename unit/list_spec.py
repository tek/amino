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

    def flat_map(self):
        List(1, 2, 3) \
            .flat_map(lambda v: [v, v + 1]) \
            .should.equal(List(1, 2, 2, 3, 3, 4))

    def flatten_maybes(self):
        List(Just(4), Empty(), Just(5), Empty()) \
            .flat_map(_.toList) \
            .should.equal(List(4, 5))

    def flat_map_maybe(self):
        List(1, 2, 3)\
            .flat_map(lambda a: Empty() if a % 2 == 0 else Just(a + 1))\
            .should.equal(List(2, 4))

    def find(self):
        l = List(1, 6, 9)
        l.find(_ % 2 == 0).should.equal(Just(6))
        l.find(_ == 3).should.equal(Empty())

    def lift(self):
        l = List(1, 4, 7)
        l.lift(1).should.equal(Just(4))
        l.lift(3).should.equal(Empty())

    def is_empty(self):
        List(1).is_empty.should_not.be.ok
        List().is_empty.should.be.ok

    def head_and_last(self):
        List(1, 2, 3).head.contains(1).should.be.ok
        List(1, 2, 3).last.contains(3).should.be.ok

    def distinct(self):
        List(1, 3, 6, 3, 6, 9, 5, 3, 6, 7, 1, 2, 5).distinct.should.equal(
            List(1, 3, 6, 9, 5, 7, 2)
        )

__all__ = ['List_']
