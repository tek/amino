from amino.test.spec_spec import Spec
from amino.tree import ListNode, LeafNode, Node, MapNode
from amino import List, _, Map
from amino.lazy_list import LazyLists


class StrNode(Node[str]):
    pass


class StrLeaf(LeafNode[str], StrNode):
    pass


class StrListNode(ListNode[str], StrNode):
    pass


class StrMapNode(MapNode[str], StrNode):
    pass


tree = StrListNode(LazyLists.cons(StrLeaf("hello"), StrListNode(LazyLists.cons(StrLeaf("sub1"), StrLeaf("sub2")))))


show_target = '''[]
 hello
 []
  sub1
  sub2'''


class TreeSpec(Spec):

    def sub(self) -> None:
        t1 = tree.lift(1)
        t1.head._data._value.should.equal('sub1')

    def flat_map(self) -> None:
        def f(n: str) -> Node:
            return StrLeaf(f'changed: {n}')
        t1 = tree.flat_map(f)
        t1.head.e.map(_._value).should.contain('changed: hello')

    def map(self) -> None:
        def f(n: str) -> Node:
            return f"changed: {n}"
        t1 = tree.map(f)
        t1.head.e.map(_._value).should.contain('changed: hello')

    def map_node(self) -> None:
        def f(n: str) -> Node:
            return f"changed: {n}"
        tree = StrMapNode(Map(first=StrListNode(List(StrLeaf('leaf1'))), second=StrLeaf('leaf2')))
        t1 = tree.map(f)
        t1.first.head.e.map(_._value).should.contain('changed: leaf1')
        t1.second.e.map(_._value).should.contain('changed: leaf2')

    def show(self) -> None:
        tree.show.should.equal(show_target)

__all__ = ('TreeSpec',)
