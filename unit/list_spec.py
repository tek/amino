import sure  # NOQA
from flexmock import flexmock  # NOQA

from fn import _

from tryp.test import Spec

from tryp import List, Empty, Just


class List_(Spec):

    def map(self):
        List(1, 2, 3) \
            .map(_ + 1) \
            .should.equal(List(2, 3, 4))

    def flat_map(self):
        List(1, 2, 3) \
            .flat_map(lambda v: [v, v + 1]) \
            .should.equal(List(1, 2, 2, 3, 3, 4))

    def flatten_maybes(self):
        List(Just(4), Empty(), Just(5), Empty())\
            .flatten\
            .should.equal(List(4, 5))

    def flat_map_maybe(self):
        List(1, 2, 3)\
            .flat_map(lambda a: Empty() if a % 2 == 0 else Just(a + 1))\
            .should.equal(List(2, 4))

    def find(self):
        l = List(1, 6, 9)
        l.find(_ % 2 == 0).should.equal(Just(6))
        l.find(_ == 3).should.equal(Empty())

    def contains(self):
        l = List(1, 6, 9)
        l.contains(6).should.be.ok
        l.contains(5).should_not.be.ok

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

    def split(self):
        z = List(5, 2, 8, 2, 9, 4, 1, 7)
        l, r = z.split(_ >= 5)
        l.should.equal(List(5, 8, 9, 7))
        r.should.equal(List(2, 2, 4, 1))

    def split_type(self):
        z = List('a', 2, 'b', 'c', 3)
        l, r = z.split_type(str)
        l.should.equal(List('a', 'b', 'c'))
        r.should.equal(List(2, 3))

    def fold_left(self):
        List(1, 2, 3).fold_left('')(lambda a, b: str(b) + a)\
            .should.equal('321')

    def fold_map(self):
        List(1, 2, 3).fold_map(5, _ * 2).should.equal(17)

__all__ = ['List_']
