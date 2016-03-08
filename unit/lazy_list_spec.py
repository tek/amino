import itertools

from tryp.test import Spec
from tryp.lazy_list import LazyList
from tryp import List, _


class LazyList_(Spec):

    def slice_infinite(self):
        l = LazyList(itertools.count(), chunk_size=20)
        l[:15].should.have.length_of(15)
        l._strict.should.have.length_of(20)
        l[:20].should.have.length_of(20)
        l._strict.should.have.length_of(20)
        l[:21].should.have.length_of(21)
        l._strict.should.have.length_of(40)

    def slice_finite(self):
        l = LazyList(List.wrap(range(30)), chunk_size=20)
        l[:15].should.have.length_of(15)
        l._strict.should.have.length_of(20)
        l[:20].should.have.length_of(20)
        l._strict.should.have.length_of(20)
        l[:21].should.have.length_of(21)
        l._strict.should.have.length_of(30)

    def single(self):
        l = LazyList(List.wrap(range(30)), chunk_size=20)
        l[19].should.equal(19)
        l._strict.should.have.length_of(20)
        l[20].should.equal(20)
        l._strict.should.have.length_of(30)

    def map(self):
        l = LazyList(itertools.count(), chunk_size=20)
        l2 = l.map(_ * 10)
        l2[:5].should.equal(List.wrap(range(0, 50, 10)))

    def with_index(self):
        l = LazyList(itertools.count(), chunk_size=20)
        l2 = l.map(_ * 5).with_index
        l2[:2].should.equal(List((0, 0), (1, 5)))

    def index_of(self):
        l = LazyList(List.wrap(range(30)), chunk_size=20)
        l.index_of(21).should.contain(21)
        l.index_of(49).should.be.empty

    def find(self):
        l = LazyList(List.wrap(range(30)), chunk_size=20)
        l.find(21).should.contain(21)
        l.find(49).should.be.empty

    def deep(self):
        n = int(1e4)
        l = LazyList(List.wrap(range(n)))
        l.index_of(n - 1).should.contain(n - 1)

__all__ = ('LazyList_',)
