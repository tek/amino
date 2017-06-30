import itertools

from amino.test.spec_spec import Spec
from amino import LazyList, List, _, Just, Maybe, Task, I


class LazyListSpec(Spec):

    def slice_infinite(self) -> None:
        l = LazyList(itertools.count(), chunk_size=20)
        l[:15].should.have.length_of(15)
        l.strict.should.have.length_of(20)
        l[:20].should.have.length_of(20)
        l.strict.should.have.length_of(20)
        l[:21].should.have.length_of(21)
        l.strict.should.have.length_of(40)

    def slice_finite(self) -> None:
        l = LazyList(range(30), chunk_size=20)
        l[:15].should.have.length_of(15)
        l.strict.should.have.length_of(20)
        l[:20].should.have.length_of(20)
        l.strict.should.have.length_of(20)
        l[:21].should.have.length_of(21)
        l.strict.should.have.length_of(30)

    def single(self) -> None:
        l = LazyList(range(30), chunk_size=20)
        l[19].should.equal(19)
        l.strict.should.have.length_of(20)
        l[20].should.equal(20)
        l.strict.should.have.length_of(30)

    def map(self) -> None:
        l = LazyList(itertools.count(), chunk_size=20)
        l.lift(5)
        l2 = l.map(_ * 10)
        l2[:5].should.equal(List.wrap(range(0, 50, 10)))

    def with_index(self) -> None:
        l = LazyList(itertools.count(), chunk_size=20)
        l2 = l.map(_ * 5).with_index
        l2[:2].should.equal(List((0, 0), (1, 5)))

    def index_of(self) -> None:
        l = LazyList(range(30), chunk_size=20)
        l.index_of(21).should.contain(21)
        l.index_of(49).should.be.empty

    def find(self) -> None:
        l = LazyList(range(30), chunk_size=20)
        l.find(_ == 21).should.contain(21)
        l.find(_ == 49).should.be.empty

    def deep(self) -> None:
        n = int(1e4)
        l = LazyList(List.wrap(range(n)))
        l.index_of(n - 1).should.contain(n - 1)

    def filter(self) -> None:
        l = LazyList(range(30))
        l2 = l.filter(_ % 2 == 0)
        l2.strict.should.have.length_of(0)
        l3 = LazyList(range(30))
        l3[29]
        l4 = l3.filter(_ % 2 == 0)
        l4.strict.should.have.length_of(15)
        l4.drain.should.equal(List.wrap(range(0, 30, 2)))

    def fold_left(self) -> None:
        LazyList((1, 2, 3)).fold_left('')(lambda a, b: str(b) + a)\
            .should.equal('321')

    def fold_map(self) -> None:
        LazyList((1, 2, 3)).fold_map(5, _ * 2).should.equal(17)

    def sequence(self) -> None:
        n = 3
        l = LazyList(map(Just, range(n)))
        target = LazyList(List.wrap(range(n)))
        (l.sequence(Maybe) / _.drain).should.contain(target.drain)

    def traverse_task(self) -> None:
        n = 3
        l = LazyList(range(n))
        result = l.traverse(Task.now, Task).attempt / _.drain
        result.should.contain(l.drain)

    def zip(self) -> None:
        a = 1
        b = 2
        ab = (a, b)
        l1 = LazyList((a, a, a, a), chunk_size=1)
        l2 = LazyList((b, b, b, b), chunk_size=1)
        l1[1]
        z = l1 & l2
        z.strict.should.equal(List(ab, ab))
        z.drain.should.equal(List(ab, ab, ab, ab))

    def apzip(self) -> None:
        l = LazyList((1, 2, 3), chunk_size=1)
        l[0]
        z = l.apzip(_ + 2)
        z.drain.should.equal(List((1, 3), (2, 4), (3, 5)))

    def flat_map(self) -> None:
        l = LazyList((LazyList((1, 2, 3)), LazyList((1, 2, 3)), LazyList((1, 2, 3))))
        l.lift(1)
        l.flat_map(I).drain.should.equal(List(1, 2, 3, 1, 2, 3, 1, 2, 3))

__all__ = ('LazyListSpec',)
