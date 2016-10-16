import itertools
import typing
import random
import string
from typing import TypeVar, Callable, Generic, Iterable, Any
from functools import reduce

from toolz.itertoolz import cons

from amino import maybe, boolean
from amino.logging import log
from amino.tc.base import ImplicitsMeta, Implicits
from amino.func import curried, I
from amino.util.string import safe_string

A = TypeVar('A', covariant=True)
B = TypeVar('B')


def flatten(l: Iterable[Iterable[A]]) -> Iterable[A]:
    return list(itertools.chain.from_iterable(l))  # type: ignore


class ListMeta(ImplicitsMeta):

    def __instancecheck__(self, instance):
        if type(instance) is list:
            return False
        else:
            return super().__instancecheck__(instance)

    def __subclasscheck__(self, subclass):
        if subclass is list:
            return False
        return super().__subclasscheck__(subclass)


class List(typing.List[A], Generic[A], Implicits, implicits=True,
           metaclass=ListMeta):

    def __init__(self, *elements):
        typing.List.__init__(self, elements)

    def __getitem__(self, arg):
        s = super().__getitem__(arg)
        return List.wrap(s) if isinstance(arg, slice) else s

    @staticmethod
    def wrap(l: Iterable[B]) -> 'List[B]':
        return List(*list(l))

    @staticmethod
    def range(*a):
        return List.wrap(range(*a))

    @staticmethod
    def random_string(num: int=10):
        from amino.anon import _
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(num))

    @staticmethod
    def gen(num: int, f: Callable[[], A]):
        return List.range(num) // (lambda a: f())

    @staticmethod
    def lines(data: str):
        return List.wrap(data.splitlines())

    def lift(self, index: int) -> 'maybe.Maybe[A]':
        return (
            (maybe.Just(self[index]) if len(self) > index else maybe.Empty())
            if index >= 0 else
            (maybe.Just(self[index]) if len(self) >= -index else maybe.Empty())
        )

    def lift_all(self, index, *indexes):
        from amino.anon import _
        def folder(z, n):
            return n.ap(z / _.cat)
        els = List.wrap(indexes) / self.lift
        init = self.lift(index) / List
        return els.fold_left(init)(folder)

    def smap(self, f: Callable[..., B]) -> 'List[B]':
        return List.wrap(list(itertools.starmap(f, self)))

    def flat_smap(self, f: Callable[..., 'Iterable[B]']) -> 'List[B]':
        return List.wrap(flatten(list(itertools.starmap(f, self))))

    def foreach(self, f: Callable[[A], B]) -> None:
        for el in self:
            f(el)

    def forall(self, f: Callable[[A], bool]) -> boolean.Boolean:
        return boolean.Boolean(all(f(el) for el in self))

    def contains(self, value):
        return value in self

    def exists(self, f: Callable[[A], bool]) -> bool:
        return self.find(f).is_just

    @property
    def is_empty(self):
        return boolean.Boolean(self.length == 0)

    empty = is_empty

    @property
    def length(self):
        return len(self)

    @property
    def head(self):
        return self.lift(0)

    @property
    def last(self):
        return self.lift(-1)

    @property
    def init(self):
        return maybe.Empty() if self.empty else maybe.Just(self[:-1])

    @property
    def tail(self):
        return maybe.Empty() if self.empty else maybe.Just(self[1:])

    @property
    def detach_head(self):
        return self.head.product(self.tail)

    @property
    def detach_last(self):
        return self.last.product(self.init)

    @property
    def distinct(self):
        seen = set()
        return List.wrap(x for x in self if x not in seen and not seen.add(x))

    def add(self, other: typing.List[A]) -> 'List[A]':
        return List.wrap(typing.List.__add__(self, other))

    __add__ = add

    def without(self, el) -> 'List[A]':
        from amino.anon import _
        return self.filter(_ != el)

    __sub__ = without

    def split(self, f: Callable[[A], bool]):
        def splitter(z, e):
            l, r = z
            return (l + (e,), r) if f(e) else (l, r + (e,))
        l, r = reduce(splitter, self, ((), (),))
        return List.wrap(l), List.wrap(r)

    def split_type(self, tpe: type):
        return self.split(lambda a: isinstance(a, tpe))

    def debug(self, prefix=None):
        prefix = '' if prefix is None else prefix + ' '
        log.debug(prefix + str(self))
        return self

    def index_of(self, target: Any):
        from amino.anon import _
        return self.index_where(_ == target)

    @property
    def reversed(self):
        return List.wrap(reversed(self))

    def mk_string(self, sep=''):
        return sep.join(self / str)

    @property
    def join_lines(self):
        return self.mk_string('\n')

    def cons(self, item):
        return List.wrap(cons(item, self))

    def cat(self, item):
        return self + List(item)

    @property
    def transpose(self):
        return List.wrap(map(List.wrap, zip(*self)))

    def drop(self, n: int):
        return self[n:]

    def drop_while(self, pred: Callable[[A], bool]):
        index = self.index_where(lambda a: not pred(a))
        return index / (lambda a: self[a:]) | self

    def remove_all(self, els: 'List[A]') -> 'List[A]':
        return self.filter_not(els.contains)

    def __repr__(self):
        return 'List({})'.format(', '.join(map(safe_string, self)))

    def __hash__(self):
        return hash(tuple(self))

    def sort_by(self, f: Callable[[A], bool], reverse=False):
        return List.wrap(sorted(self, key=f, reverse=reverse))

    def sort(self, reverse=False):
        return self.sort_by(I, reverse)

    def replace_item(self, a, b) -> 'List[A]':
        return self.map(lambda c: b if c == a else c)

    @curried
    def replace_where(self, a, pred: Callable):
        return self.map(lambda b: a if pred(b) else b)

    def __mul__(self, other):
        return List.wrap(super().__mul__(other))

__all__ = ('List',)
