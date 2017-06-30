import abc
from typing import Callable, TypeVar, Generic, Union, cast

from amino.logging import Logging
from amino import LazyList, Boolean, __, _, Either, Right, Maybe, Left, L, Map, curried
from amino.boolean import false, true
from amino.tc.base import Implicits
from amino.tc.flat_map import FlatMap
from amino.func import call_by_name
from amino.lazy_list import LazyLists


def indent(strings: LazyList[str]) -> LazyList[str]:
    return strings.map(' ' + _)


Data = TypeVar('Data')
A = TypeVar('A')
B = TypeVar('B')
Z = TypeVar('Z')
Key = Union[str, int]


class Node(Generic[Data], Logging, abc.ABC, Implicits, implicits=True, auto=True):

    @abc.abstractproperty
    def sub(self) -> LazyList['Node']:
        ...

    @abc.abstractproperty
    def strings(self) -> LazyList[str]:
        ...

    @property
    def show(self) -> str:
        return self.strings.mk_string('\n')

    @abc.abstractmethod
    def foreach(self, f: Callable[['Node'], None]) -> None:
        ...

    @abc.abstractmethod
    def filter(self, pred: Callable[['Node'], bool]) -> 'LazyList[Node]':
        ...

    @abc.abstractproperty
    def flatten(self) -> 'LazyList[Node]':
        ...

    @abc.abstractmethod
    def contains(self, target: 'Node') -> Boolean:
        ...

    @abc.abstractmethod
    def lift(self, key: Key) -> 'SubTree':
        ...

    def __getitem__(self, key: Key) -> 'SubTree':
        return self.lift(key)

    def __getattr__(self, key: Key) -> 'SubTree':
        try:
            return super().__getattr__(key)
        except AttributeError:
            return self.lift(key)

    @abc.abstractproperty
    def empty(self) -> Boolean:
        ...

    @curried
    def fold_left(self, z: Z, f: Callable[[Z, 'Node'], Z]) -> Z:
        z1 = f(z, self)
        return self.sub.fold_left(z1)(lambda z2, a: a.fold_left(z2)(f))


class SubTree(Implicits, implicits=True, auto=True):

    @staticmethod
    def cons(fa: Node, key: Key) -> 'SubTree':
        return (  # type: ignore
            cast(SubTree, SubTreeList(fa, key))
            if isinstance(fa, ListNode) else
            SubTreeLeaf(fa, key)
            if isinstance(fa, LeafNode) else
            SubTreeMap(fa, key)
        )

    @staticmethod
    def from_maybe(data: Maybe[Node], key: Key, err: str) -> 'SubTree':
        return data.cata(SubTree.cons, SubTreeInvalid(key, err))

    def __getattr__(self, key: Key) -> 'SubTree':
        try:
            return super().__getattr__(key)
        except AttributeError:
            return self._getattr(key)

    @abc.abstractmethod
    def _getattr(self, key: Key) -> 'SubTree':
        ...

    def __getitem__(self, key: Key) -> 'SubTree':
        return self._getitem(key)

    @abc.abstractmethod
    def _getitem(self, key: Key) -> 'SubTree':
        ...

    def cata(self, f: Callable[[Node], A], b: Union[A, Callable[[], A]]) -> A:
        return (
            f(self.data)
            if isinstance(self, SubTreeValid)
            else call_by_name(b)
        )

    @abc.abstractproperty
    def e(self) -> Either[str, Node]:
        ...

    @abc.abstractproperty
    def valid(self) -> Boolean:
        ...

    @abc.abstractproperty
    def strings(self) -> LazyList[str]:
        ...

    @abc.abstractproperty
    def show(self) -> LazyList[str]:
        ...


class Inode(Generic[Data], Node[Data]):

    @abc.abstractproperty
    def sub(self) -> LazyList[Node]:
        ...

    def foreach(self, f: Callable[[Node], None]) -> None:
        f(self)
        self.sub.foreach(__.foreach(f))

    @property
    def flatten(self) -> LazyList[Node]:
        return self.sub.flat_map(_.flatten).cons(self)

    def contains(self, target: Node) -> Boolean:
        return self.sub.contains(target)

    @property
    def empty(self) -> Boolean:
        return self.data.empty


class ListNode(Generic[Data], Inode[Data]):

    def __init__(self, sub: LazyList[Node[Data]]) -> None:
        self.data = sub

    @property
    def sub(self) -> LazyList[Node[Data]]:
        return self.data

    @property
    def _desc(self) -> str:
        return '[]'

    @property
    def strings(self) -> LazyList[str]:
        return indent(self.sub // (lambda a: a.strings)).cons(self._desc)

    @property
    def head(self) -> 'SubTree':
        return self.lift(0)

    @property
    def last(self) -> 'SubTree':
        return self.lift(-1)

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self.sub.map(str).mk_string(','))

    def __repr__(self) -> str:
        return str(self)

    def lift(self, key: Key) -> SubTree:
        return (
            SubTreeInvalid(key, 'ListNode index must be int')
            if isinstance(key, str) else
            self.sub.lift(key) / L(SubTree.cons)(_, key) | (lambda: SubTreeInvalid(key, 'StrListNode index oob'))
        )

    def copy(self, sub: LazyList[Node]) -> Node:
        return ListNode(sub)

    def filter(self, pred: Callable[[Node], bool]) -> Node:
        def filt(n: Node) -> bool:
            return (
                pred(n)
                if isinstance(n, LeafNode) else
                not n.empty
            )
        return self.copy(self.sub.map(__.filter(pred)).filter(filt))


class MapNode(Generic[Data], Inode[Data]):

    def __init__(self, sub: Map[str, Node[Data]]) -> None:
        self.data = sub

    @property
    def sub(self) -> LazyList[Node[Data]]:
        return LazyList(self.data.v)

    @property
    def _desc(self) -> str:
        return '{}'

    @property
    def strings(self) -> LazyList[str]:
        return indent(self.sub // (lambda a: a.strings)).cons(self._desc)

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self.sub)

    def __repr__(self) -> str:
        return str(self)

    def lift(self, key: Key) -> SubTree:
        def err() -> SubTree:
            keys = ', '.join(self.data.keys())
            return SubTreeInvalid(key, f'MapNode invalid key ({keys})')
        return (
            self.data.lift(key) /
            L(SubTree.cons)(_, key) |
            err
        )

    def copy(self, sub: Map[str, Node]) -> Node:
        return MapNode(sub)

    def filter(self, pred: Callable[[Node], bool]) -> Node:
        def filt(n: Node) -> bool:
            return (
                pred(n)
                if isinstance(n, LeafNode) else
                not n.empty
            )
        return self.copy(self.data.valmap(__.filter(pred)).valfilter(filt))


class LeafNode(Generic[Data], Node[Data]):

    def __init__(self, value: Data) -> None:
        self.data = value

    @property
    def strings(self) -> LazyList[Data]:
        return LazyLists.cons(self.data)

    @property
    def sub(self) -> LazyList[Node]:
        return LazyList([])

    def foreach(self, f: Callable[[Node], None]) -> None:
        f(self)

    def filter(self, pred: Callable[[Node], bool]) -> Node:
        return self

    @property
    def flatten(self) -> LazyList[Node]:
        return LazyLists.cons(self)

    def contains(self, target: Node) -> Boolean:
        return false

    def lift(self, key: Key) -> 'SubTree':
        return SubTreeInvalid(key, 'LeafNode cannot be indexed')

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self.data)

    def __repr__(self) -> str:
        return str(self)

    @property
    def empty(self) -> Boolean:
        return false


class TreeFlatMap(FlatMap, tpe=Node):

    def map(self, fa: Node[A], f: Callable[[A], B]) -> Node[B]:
        return (
            self.map_inode(fa, f)
            if isinstance(fa, Inode) else
            self.map_leaf(fa, f)
        )

    def flat_map(self, fa: Node[A], f: Callable[[A], Node[B]]) -> Node[B]:
        return (
            self.flat_map_inode(fa, f)
            if isinstance(fa, Inode) else
            self.flat_map_leaf(fa, f)
        )

    def flat_map_inode(self, fa: Inode[A], f: Callable[[A], Node[B]]) -> Node[B]:
        def err() -> Inode[A]:
            raise Exception(f'invalid sub for `Tree.flat_map_inode`: {fa}')
        return (
            self.flat_map_map(fa, f)
            if isinstance(fa, MapNode) else
            self.flat_map_list(fa, f)
            if isinstance(fa, ListNode) else
            err()
        )

    def flat_map_map(self, fa: MapNode[A], f: Callable[[A], Node[B]]) -> Node[B]:
        return MapNode(fa.sub.map(lambda a: self.flat_map(a, f)))

    def flat_map_list(self, fa: ListNode[A], f: Callable[[A], Node[B]]) -> Node[B]:
        return ListNode(fa.sub.map(lambda a: self.flat_map(a, f)))

    def flat_map_leaf(self, fa: LeafNode[A], f: Callable[[A], Node[B]]) -> Node[B]:
        return f(fa.data)

    def map_inode(self, fa: Inode[A], f: Callable[[A], B]) -> Node[B]:
        def err() -> Inode[A]:
            raise Exception(f'invalid sub for `Tree.map_inode`: {fa}')
        return (
            self.map_map(fa, f)
            if isinstance(fa, MapNode) else
            self.map_list(fa, f)
            if isinstance(fa, ListNode) else
            err()
        )

    def map_map(self, fa: MapNode[A], f: Callable[[A], B]) -> Node[B]:
        return MapNode(fa.data.valmap(lambda a: self.map(a, f)))

    def map_list(self, fa: ListNode[A], f: Callable[[A], B]) -> Node[B]:
        return ListNode(fa.sub.map(lambda a: self.map(a, f)))

    def map_leaf(self, fa: LeafNode[A], f: Callable[[A], B]) -> Node[B]:
        return LeafNode(f(fa.data))


class SubTreeValid(SubTree):

    def __init__(self, data: Node, key: Key) -> None:
        self.data = data
        self._key = key

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self.data)

    @property
    def e(self) -> Either[str, Node]:
        return Right(self.data)

    @property
    def valid(self) -> Boolean:
        return true

    @property
    def strings(self) -> LazyList[str]:
        return self.data.strings

    @property
    def show(self) -> str:
        return self.data.show


class SubTreeList(SubTreeValid):

    @property
    def head(self) -> SubTree:
        return self[0]

    @property
    def last(self) -> SubTree:
        return self[-1]

    def _getattr(self, key: Key) -> SubTree:
        return SubTreeInvalid(key, 'cannot access attrs in SubTreeList')

    def _getitem(self, key: Key) -> SubTree:
        return self.data.lift(key)

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self.data.sub.drain.join_comma)

    @property
    def _keys(self) -> LazyList[str]:
        return self.data.k


class SubTreeLeaf(SubTreeValid):

    def err(self, key: Key) -> SubTree:
        return SubTreeInvalid(key, 'cannot access attrs in SubTreeLeaf')

    def _getattr(self, key: Key) -> SubTree:
        return self.err(key)

    def _getitem(self, key: Key) -> SubTree:
        return self.err(key)


class SubTreeMap(SubTreeValid):

    def _getattr(self, key: Key) -> SubTree:
        return self.data.lift(key)

    def _getitem(self, key: Key) -> SubTree:
        return self.data.lift(key)

    @property
    def _keys(self) -> LazyList[str]:
        return self.data.k


class SubTreeInvalid(SubTree):

    def __init__(self, key: Key, reason: str) -> None:
        self.key = key
        self.reason = reason

    def __str__(self) -> str:
        s = 'SubTreeInvalid({}, {})'
        return s.format(self.key, self.reason)

    def __repr__(self) -> str:
        return str(self)

    @property
    def valid(self) -> Boolean:
        return false

    @property
    def _error(self) -> str:
        return 'no subtree `{}`: {}'.format(self.key, self.reason)

    def _getattr(self, key: Key) -> SubTree:
        return self

    def _getitem(self, key: Key) -> SubTree:
        return self

    @property
    def e(self) -> Either[str, Node]:
        return Left(self._error)

    @property
    def strings(self) -> LazyList[str]:
        return LazyList([])

    @property
    def show(self) -> LazyList[str]:
        return str(self)

__all__ = ('Node', 'Inode', 'LeafNode')
