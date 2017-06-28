import abc
from typing import Callable, TypeVar, Generic, Union, cast

from amino.logging import Logging
from amino import List, Boolean, __, _, Either, Right, Maybe, Left, L, Map
from amino.boolean import false, true
from amino.tc.base import Implicits
from amino.tc.flat_map import FlatMap
from amino.func import call_by_name


def indent(strings: List[str]) -> List[str]:
    return strings.map(' ' + _)


Data = TypeVar('Data')
A = TypeVar('A')
B = TypeVar('B')
Key = Union[str, int]


class Node(Generic[Data], Logging, abc.ABC, Implicits, implicits=True, auto=True):

    def __init__(self, data: Data, parent: 'Node') -> None:
        self.data = data
        self.parent = parent

    @abc.abstractproperty
    def sub(self) -> List['Node']:
        ...

    @abc.abstractproperty
    def strings(self) -> List[str]:
        ...

    @property
    def show(self) -> str:
        return self.strings.mk_string('\n')

    @abc.abstractmethod
    def foreach(self, f: Callable[['Node'], None]) -> None:
        ...

    @abc.abstractmethod
    def filter(self, pred: Callable[['Node'], bool]) -> 'List[Node]':
        ...

    def _filter(self, pred: Callable[['Node'], bool]) -> 'List[Node]':
        return Boolean(pred(self)).maybe(self).to_list

    @abc.abstractproperty
    def flatten(self) -> 'List[Node]':
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


class SubTree:

    @staticmethod
    def cons(fa: Node, key: Key) -> 'SubTree':
        return (
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
            f(self._data)
            if isinstance(self, SubTreeValid)
            else call_by_name(b)
        )

    @abc.abstractproperty
    def e(self) -> Either[str, Node]:
        ...

    @abc.abstractproperty
    def valid(self) -> Boolean:
        ...


class Inode(Generic[Data], Node[Data]):

    @abc.abstractproperty
    def sub(self) -> List[Node]:
        ...

    def foreach(self, f: Callable[[Node], None]) -> None:
        f(self)
        self.sub.foreach(__.foreach(f))

    def filter(self, pred: Callable[[Node], bool]) -> List[Node]:
        return self._filter(pred) + self.sub.flat_map(__.filter(pred))

    @property
    def flatten(self) -> List[Node]:
        yield self
        for a in self.sub:
            yield from a.flatten

    def contains(self, target: Node) -> Boolean:
        return self.sub.contains(target)


class ListNode(Generic[Data], Inode[Data]):

    def __init__(self, sub: List[Node[Data]]) -> None:
        self._sub = sub

    @property
    def sub(self) -> List[Node[Data]]:
        return self._sub

    @property
    def _desc(self) -> str:
        return '[]'

    @property
    def strings(self) -> List[str]:
        return indent(self.sub // _.strings).cons(self._desc)

    @property
    def head(self) -> 'SubTree':
        return self.lift(0)

    @property
    def last(self) -> 'SubTree':
        return self.lift(-1)

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self._sub.map(str).mk_string(','))

    def __repr__(self) -> str:
        return str(self)

    def lift(self, key: Key) -> SubTree:
        return (
            SubTreeInvalid(key, 'ListNode index must be int')
            if isinstance(key, str) else
            self._sub.lift(key) / L(SubTree.cons)(_, key) | (lambda: SubTreeInvalid(key, 'StrListNode index oob'))
        )


class MapNode(Generic[Data], Inode[Data]):

    def __init__(self, sub: Map[str, Node[Data]]) -> None:
        self._sub = sub

    @property
    def sub(self) -> List[Node[Data]]:
        return self._sub.v

    @property
    def _desc(self) -> str:
        return '{}'

    @property
    def strings(self) -> List[str]:
        return indent(self.sub // _.strings).cons(self._desc)

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self._sub)

    def __repr__(self) -> str:
        return str(self)

    def lift(self, key: Key) -> SubTree:
        return (
            self._sub.lift(key) /
            L(SubTree.cons)(_, key) |
            (lambda: SubTreeInvalid(key, 'MapListNode invalid index'))
        )


class LeafNode(Generic[Data], Node[Data]):

    def __init__(self, value: Data) -> None:
        self.value = value

    @property
    def strings(self) -> List[Data]:
        return List(self.value)

    @property
    def sub(self) -> List[Node]:
        return List()

    def foreach(self, f: Callable[[Node], None]) -> None:
        f(self)

    def filter(self, pred: Callable[[Node], bool]) -> List[Node]:
        return self._filter(pred)

    @property
    def flatten(self) -> List[Node]:
        yield self

    def contains(self, target: Node) -> Boolean:
        return false

    def lift(self, key: Key) -> 'SubTree':
        return SubTreeInvalid(key, 'LeafNode cannot be indexed')

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self.value)

    def __repr__(self) -> str:
        return str(self)


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
        return f(fa.value)

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
        return MapNode(fa._sub.valmap(lambda a: self.map(a, f)))

    def map_list(self, fa: ListNode[A], f: Callable[[A], B]) -> Node[B]:
        return ListNode(fa._sub.map(lambda a: self.map(a, f)))

    def map_leaf(self, fa: LeafNode[A], f: Callable[[A], B]) -> Node[B]:
        return LeafNode(f(fa.value))


class SubTreeValid(Generic[A], SubTree):

    def __init__(self, data: A, key: Key) -> None:
        self._data = data
        self._key = key

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self._data)

    @property
    def e(self) -> Either[str, Node]:
        return Right(self._data)

    @property
    def valid(self) -> Boolean:
        return true


class SubTreeList(SubTreeValid[ListNode]):

    @property
    def head(self) -> SubTree:
        return self[0]

    @property
    def last(self) -> SubTree:
        return self[-1]

    def _getattr(self, key: Key) -> SubTree:
        return SubTreeInvalid(key, 'cannot access attrs in SubTreeList')

    def _getitem(self, key: Key) -> SubTree:
        return self._data.lift(key)

    def __str__(self) -> str:
        return '{}({})'.format(self.__class__.__name__, self._data._sub.join_comma)

    @property
    def _keys(self) -> List[str]:
        return self._data.k


class SubTreeLeaf(SubTreeValid[LeafNode]):

    def err(self, key: Key) -> SubTree:
        return SubTreeInvalid(key, 'cannot access attrs in SubTreeLeaf')

    def _getattr(self, key: Key) -> SubTree:
        return self.err(key)

    def _getitem(self, key: Key) -> SubTree:
        return self.err(key)


class SubTreeMap(SubTreeValid[MapNode]):

    def _getattr(self, key: Key) -> SubTree:
        return self._data.lift(key)

    def _getitem(self, key: Key) -> SubTree:
        return self._data.lift(key)

    @property
    def _keys(self) -> List[str]:
        return self._data.k


class SubTreeInvalid(SubTree):

    def __init__(self, key: Key, reason: str) -> None:
        self.key = key
        self.reason = reason

    def __str__(self) -> str:
        s = 'SubTreeInvalid({}, {})'
        return s.format(self.key, self.reason)

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

__all__ = ('Node', 'Inode', 'LeafNode')
