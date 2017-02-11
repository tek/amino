import itertools
import typing
import random
import string
from functools import reduce
from typing import TypeVar, Callable, Generic, Iterable, Any

from toolz.itertoolz import cons, groupby

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

    # def __subclasscheck__(self, subclass):
    #     if subclass is list:
    #         return False
    #     return super().__subclasscheck__(subclass)


def _rand_str(chars, num: int=10):
    return ''.join(random.choice(chars) for i in range(num))


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
        chars = string.ascii_letters + string.digits
        return _rand_str(chars, num)

    @staticmethod
    def random_alpha(num: int=10):
        chars = string.ascii_letters
        return _rand_str(chars, num)

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
    def nonempty(self) -> boolean.Boolean:
        return not self.empty

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
    def distinct(self) -> 'List[A]':
        return self.distinct_by(I)

    def distinct_by(self, f: Callable[[A], bool]) -> 'List[A]':
        seen = set()  # type: set
        def pred(a):
            v = f(a)
            return v in seen or seen.add(v)
        return List.wrap(x for x in self if not pred(x))

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

    def mk_string(self, sep: str='') -> str:
        return sep.join(self / str)

    @property
    def join_lines(self) -> str:
        return self.mk_string('\n')

    @property
    def join_comma(self) -> str:
        return self.mk_string(', ')

    @property
    def join_tokens(self) -> str:
        return self.mk_string(' ')

    @property
    def join_dot(self) -> str:
        return self.mk_string('.')

    def cons(self, item):
        return List.wrap(cons(item, self))

    def cat(self, item):
        return self + List(item)

    def cat_m(self, item: maybe.Maybe):
        return item / self.cat | self

    @property
    def transpose(self):
        return List.wrap(map(List.wrap, zip(*self)))

    def drop(self, n: int) -> 'List[A]':
        return self[n:]

    def take(self, n: int):
        return self[:n]

    def drop_while(self, pred: Callable[[A], bool]):
        index = self.index_where(lambda a: not pred(a))
        return index / (lambda a: self[a:]) | self

    def drop_right(self, n: int) -> 'List[A]':
        return self.take(self.length - n)

    def remove_all(self, els: 'List[A]') -> 'List[A]':
        return self.filter_not(els.contains)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               ', '.join(map(repr, self)))

    def __str__(self):
        return '[{}]'.format(', '.join(map(safe_string, self)))

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

    def group_by(self, f):
        from amino import Map
        return Map(groupby(f, self)).valmap(List.wrap)

    def slice(self, start: int, end: int) -> 'List[A]':
        return self[start:end]


class Lists:

    wrap = List.wrap
    range = List.range
    random_string = List.random_string
    random_alpha = List.random_alpha
    gen = List.gen
    lines = List.lines

    @staticmethod
    def split(data: str, splitter: str, maxsplit: int=-1) -> List[str]:
        return List.wrap(data.split(splitter, maxsplit))

    @staticmethod
    def rsplit(data: str, splitter: str, maxsplit: int=-1) -> List[str]:
        return List.wrap(data.rsplit(splitter, maxsplit))

__all__ = ('List',)
