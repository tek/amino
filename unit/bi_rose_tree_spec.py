from amino.test.spec_spec import Spec
from amino.bi_rose_tree import RoseTree, nodes, leaves, from_tree
from amino import _, __, List

from unit.tree_spec import mtree


simple_tree = RoseTree(1, nodes((2, leaves(3, 4))))

class BiRoseTreeSpec(Spec):

    def show(self) -> None:
        simple_tree.show.should.equal('1\n 2\n  3\n  4')

    def map(self) -> None:
        t1 = simple_tree.map(_ + 2)
        t1[0].flat_map(_[1]).map(_.data).should.contain(6)
        t1[0].flat_map(_[1]).map(_.parent.parent).should.contain(t1)

    def filter(self) -> None:
        t1 = simple_tree.filter(_ <= 3)
        t1[0].map(__.sub.drain.map(_.data)).should.contain(List(3))

    def from_tree(self) -> None:
        t1 = from_tree(mtree)
        t1[0].flat_map(_.parent[0]).map(_.sub.drain.length).should.contain(2)

__all__ = ('BiRoseTreeSpec',)
