from typing import Generic, TypeVar, Callable, Tuple, Any

from amino import LazyList, _, Maybe, I
from amino.lazy import lazy
from amino.lazy_list import LazyLists
from amino.tree import indent, Node


Data = TypeVar('Data')
A = TypeVar('A')
B = TypeVar('B')


class RoseTree(Generic[Data]):

    def __init__(self, data: Data, sub_cons: Callable[['RoseTree[Data]'], LazyList['RoseTree[Data]']]) -> None:
        self.data = data
        self._sub_cons = sub_cons

    @lazy
    def sub(self) -> LazyList['RoseTree[Data]']:
        return self._sub_cons(self)

    def __str__(self) -> str:
        num = self.sub.drain.length
        return f'{self.__class__.__name__}({self.data}, {num} children)'

    def __repr__(self) -> str:
        return str(self)

    @property
    def show(self) -> str:
        return self.strings.drain.mk_string('\n')

    @property
    def strings(self) -> LazyList[str]:
        return indent(self.sub.flat_map(_.strings)).cons(str(self.data))

    def map(self, f: Callable[[Data], A]) -> 'RoseTree[A]':
        return self.copy(f, I)  # type: ignore

    def copy(self, f: Callable[[Data], A], g: Callable[[LazyList['RoseTree[Data]']], LazyList['RoseTree[A]']]
             ) -> 'RoseTree[A]':
        return RoseTree(f(self.data), self._copy_sub(f, g))

    def _copy_sub(self, f: Callable[[Data], A], g: Callable[[LazyList['RoseTree[Data]']], LazyList['RoseTree[A]']]
                  ) -> Callable[['RoseTree[A]'], LazyList['RoseTree[A]']]:
        def sub(node: RoseTree[Data]) -> Callable[[RoseTree[A]], RoseTree[A]]:
            return lambda parent: BiRoseTree(f(node.data), parent, node._copy_sub(f, g))
        return lambda parent: g(self.sub).map(lambda a: sub(a)(parent))

    def __getitem__(self, key: int) -> Maybe['RoseTree[Data]']:
        return self.sub.lift(key)

    def filter(self, f: Callable[[Data], bool]) -> 'RoseTree[Data]':
        return self.copy(I, lambda a: a.filter(lambda n: f(n.data)))


class BiRoseTree(Generic[Data], RoseTree[Data]):

    def __init__(
            self,
            data: Data,
            parent: RoseTree[Data],
            sub_cons: Callable[[RoseTree[Data]], LazyList[RoseTree[Data]]]
    ) -> None:
        super().__init__(data, sub_cons)
        self.parent = parent


def node(data: Data, sub_cons: Callable[[RoseTree[Data]], LazyList[RoseTree[Data]]]
         ) -> Callable[[RoseTree[Data]], RoseTree[Data]]:
    return lambda parent: BiRoseTree(data, parent, sub_cons)


def nodes(*s: Tuple[Data, Callable[[RoseTree[Data]], RoseTree[Data]]]
          ) -> Callable[[RoseTree[Data]], LazyList[RoseTree[Data]]]:
    return lambda parent: LazyList(s).map2(node).map(lambda f: f(parent))


def leaf(data: Data) -> Callable[[RoseTree[Data]], RoseTree[Data]]:
    return lambda parent: BiRoseTree(data, parent, lambda a: LazyLists.empty())


def leaves(*data: Data) -> Callable[[RoseTree[Data]], LazyList[RoseTree[Data]]]:
    return lambda parent: LazyList(data).map(leaf).map(lambda f: f(parent))


def from_tree(tree: Node[A, Any], f: Callable[[Node[A, Any]], B]) -> RoseTree[B]:
    def sub(node: Node[A, Any]) -> Callable[[RoseTree[Node[A, Any]]], LazyList[RoseTree[Node[A, Any]]]]:
        return lambda parent: node.sub_l.map(lambda a: BiRoseTree(f(a), parent, sub(a)))
    return RoseTree(f(tree), sub(tree))

__all__ = ('BiRoseTree', 'RoseTree', 'node', 'leaf', 'leaves')
