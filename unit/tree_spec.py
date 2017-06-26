from typing import TypeVar

from amino.test.spec_spec import Spec
from amino.tree import (ListNode, LeafNode, Node, Tree, Key, SubTree, SubTreeInvalid, SubTreeList, SubTreeLeaf, MapNode,
                        SubTreeMap, Inode)
from amino import List, L, _, Map


class StrNode(Node[str]):

    @property
    def tpe(self) -> type:
        return StrNode


class StrLeaf(LeafNode[str], StrNode):
    pass


class StrListNode(ListNode[str], StrNode):
    pass


class StrMapNode(MapNode[str], StrNode):
    pass


F = TypeVar('F')


class StrTree(Tree, tpe=StrNode):

    def leaf(self, a: str) -> Node[str]:
        return StrLeaf(a)

    def list_node(self, sub: List[Node[str]]) -> Node[str]:
        return StrListNode(sub)

    def map_node(self, sub: Map[Key, Node[str]]) -> Node[str]:
        return StrMapNode(sub)

    def sub(self, fa: Node[str], key: Key) -> SubTree:
        return self.inode_sub(fa, key) if isinstance(fa, Inode) else SubTreeInvalid(key, f'{fa} cannot lift')

    def inode_sub(self, fa: Inode[str], key: Key) -> SubTree:
        return self.list_sub(fa, key) if isinstance(fa, StrListNode) else self.map_sub(fa, key)

    def list_sub(self, fa: StrListNode, key: Key) -> SubTree:
        return (
            SubTreeInvalid(key, 'ListNode index must be int')
            if isinstance(key, str) else
            fa._sub.lift(key) / L(self.cons_sub)(_, key) | (lambda: SubTreeInvalid(key, 'StrListNode index oob'))
        )

    def map_sub(self, fa: StrMapNode, key: Key) -> SubTree:
        return fa._sub.lift(key) / L(self.cons_sub)(_, key) | (lambda: SubTreeInvalid(key, 'MapListNode invalid index'))

    def cons_sub(self, fa: Node, key: Key) -> SubTree:
        return (
            SubTreeList(fa, key)
            if isinstance(fa, StrListNode) else
            SubTreeLeaf(fa, key)
            if isinstance(fa, StrLeaf) else
            SubTreeMap(fa, key)
        )


tree = StrListNode(List(StrLeaf("hello"), StrListNode(List(StrLeaf("sub1"), StrLeaf("sub2")))))


class TreeSpec(Spec):

    def sub(self) -> None:
        t1 = tree.lift(1)
        t1.head._data.value.should.equal('sub1')

    def flat_map(self) -> None:
        def f(n: str) -> Node:
            return StrLeaf(f"changed: {n}")
        t1 = tree.flat_map(f)
        t1.head.e.map(_.value).should.contain("changed: hello")

    def map(self) -> None:
        def f(n: str) -> Node:
            return f"changed: {n}"
        t1 = tree.map(f)
        t1.head.e.map(_.value).should.contain("changed: hello")

    def map_node(self) -> None:
        def f(n: str) -> Node:
            return f"changed: {n}"
        tree = StrMapNode(Map(first=StrListNode(List(StrLeaf('leaf1'))), second=StrLeaf('leaf2')))
        t1 = tree.map(f)
        t1.first.head.e.map(_.value).should.contain("changed: leaf1")
        t1.second.e.map(_.value).should.contain("changed: leaf2")

__all__ = ('TreeSpec',)
