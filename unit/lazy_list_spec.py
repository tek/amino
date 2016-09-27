import itertools

from amino.test import Spec
from amino import LazyList, List, _, Just, Maybe


class LazyListSpec(Spec):

    def slice_infinite(self):
        l = LazyList(itertools.count(), chunk_size=20)
        l[:15].should.have.length_of(15)
        l.strict.should.have.length_of(20)
        l[:20].should.have.length_of(20)
        l.strict.should.have.length_of(20)
        l[:21].should.have.length_of(21)
        l.strict.should.have.length_of(40)

    def slice_finite(self):
        l = LazyList(range(30), chunk_size=20)
        l[:15].should.have.length_of(15)
        l.strict.should.have.length_of(20)
        l[:20].should.have.length_of(20)
        l.strict.should.have.length_of(20)
        l[:21].should.have.length_of(21)
        l.strict.should.have.length_of(30)

    def single(self):
        l = LazyList(range(30), chunk_size=20)
        l[19].should.equal(19)
        l.strict.should.have.length_of(20)
        l[20].should.equal(20)
        l.strict.should.have.length_of(30)

    def map(self):
        l = LazyList(itertools.count(), chunk_size=20)
        l.lift(5)
        l2 = l.map(_ * 10)
        l2[:5].should.equal(List.wrap(range(0, 50, 10)))

    def with_index(self):
        l = LazyList(itertools.count(), chunk_size=20)
        l2 = l.map(_ * 5).with_index
        l2[:2].should.equal(List((0, 0), (1, 5)))

    def index_of(self):
        l = LazyList(range(30), chunk_size=20)
        l.index_of(21).should.contain(21)
        l.index_of(49).should.be.empty

    def find(self):
        l = LazyList(range(30), chunk_size=20)
        l.find(_ == 21).should.contain(21)
        l.find(_ == 49).should.be.empty

    def deep(self):
        n = int(1e4)
        l = LazyList(List.wrap(range(n)))
        l.index_of(n - 1).should.contain(n - 1)

    def filter(self):
        l = LazyList(range(30))
        l2 = l.filter(_ % 2 == 0)
        l2.strict.should.have.length_of(0)
        l3 = LazyList(range(30))
        l3[29]
        l4 = l3.filter(_ % 2 == 0)
        l4.strict.should.have.length_of(15)
        l4.drain.should.equal(List.wrap(range(0, 30, 2)))

    def fold_left(self):
        LazyList((1, 2, 3)).fold_left('')(lambda a, b: str(b) + a)\
            .should.equal('321')

    def fold_map(self):
        LazyList((1, 2, 3)).fold_map(5, _ * 2).should.equal(17)

    def traverse(self):
        n = 3
        l = LazyList(map(Just, range(n)))
        target = LazyList(List.wrap(range(n)))
        (l.sequence(Maybe) / _.drain).should.contain(target.drain)

__all__ = ('LazyListSpec',)
