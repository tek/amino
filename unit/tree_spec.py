from typing import Generic, TypeVar, Any

from amino.test.spec_spec import Spec
from amino.tree import ListNode, LeafNode, Node, MapNode
from amino import _, Map, LazyList
from amino.lazy_list import LazyLists


Sub = TypeVar('Sub')


class StrNode(Generic[Sub], Node[str, Sub]):
    pass


class StrLeaf(LeafNode[str], StrNode[None]):
    pass


class StrListNode(ListNode[str], StrNode[LazyList[Node[str, Any]]]):
    pass


class StrMapNode(MapNode[str], StrNode[Map[str, Node[str, Any]]]):
    pass


tree = StrListNode(LazyLists.cons(StrLeaf("leaf1"), StrListNode(LazyLists.cons(StrLeaf("sub1"), StrLeaf("sub2")))))
mtree = StrMapNode(Map(first=tree, second=StrLeaf('leaf2')))


show_target = '''[]
 leaf1
 []
  sub1
  sub2'''


class TreeSpec(Spec):

    def sub(self) -> None:
        t1 = tree.lift(1)
        t1.head.data.data.should.equal('sub1')

    def flat_map(self) -> None:
        def f(n: str) -> Node:
            return StrLeaf(f'changed: {n}')
        t1 = tree.flat_map(f)
        t1.head.e.map(_.data).should.contain('changed: leaf1')

    def map(self) -> None:
        def f(n: str) -> Node:
            return f"changed: {n}"
        t1 = tree.map(f)
        t1.head.e.map(_.data).should.contain('changed: leaf1')

    def map_node(self) -> None:
        def f(n: str) -> Node:
            return f"changed: {n}"
        t1 = mtree.map(f)
        t1.s.first.head.e.map(_.data).should.contain('changed: leaf1')
        t1.s.second.e.map(_.data).should.contain('changed: leaf2')

    def show(self) -> None:
        tree.show.should.equal(show_target)

    def fold_left(self) -> None:
        def folder(z: str, a: StrNode) -> str:
            return (
                f'{z} {a.data}'
                if isinstance(a, StrLeaf) else
                z
            )
        tree.fold_left('start:')(folder).should.equal('start: leaf1 sub1 sub2')

    def filter(self) -> None:
        target = 'sub1'
        def filt(node: StrNode) -> bool:
            return isinstance(node, StrLeaf) and node.data == target
        mtree.filter(filt).s.first.head.head.e.map(_.data).should.contain(target)

__all__ = ('TreeSpec',)
