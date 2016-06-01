import itertools
import typing
from typing import TypeVar, Callable, Generic, Iterable, Any, Tuple
from functools import reduce

from toolz.itertoolz import cons

from fn import _

from tryp import maybe, boolean
from tryp.logging import log
from tryp.tc.monad import Monad
from tryp.tc.base import Implicits, ImplicitInstances, tc_prop, ImplicitsMeta
from tryp.lazy import lazy
from tryp.tc.traverse import Traverse
from tryp.func import curried

A = TypeVar('A', covariant=True)
B = TypeVar('B')


def flatten(l: Iterable[Iterable[A]]) -> Iterable[A]:
    return list(itertools.chain.from_iterable(l))  # type: ignore


class ListInstances(ImplicitInstances):

    @lazy
    def _instances(self):
        from tryp import Map
        return Map({Monad: ListMonad(), Traverse: ListTraverse()})


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

    def lift(self, index: int) -> 'maybe.Maybe[A]':
        return maybe.Maybe.from_call(self.__getitem__, index, exc=IndexError)

    def smap(self, f: Callable[..., B]) -> 'List[B]':
        return List.wrap(list(itertools.starmap(f, self)))

    def flat_smap(self, f: Callable[..., 'Iterable[B]']) -> 'List[B]':
        return List.wrap(flatten(list(itertools.starmap(f, self))))

    @property
    def flatten(self):
        return self.flat_map(lambda a: a)

    def foreach(self, f: Callable[[A], B]) -> None:
        for el in self:
            f(el)

    def forall(self, f: Callable[[A], bool]) -> boolean.Boolean:
        return boolean.Boolean(all(f(el) for el in self))

    def find(self, f: Callable[[A], bool]):
        return maybe.Maybe(next(filter(f, self), None))

    def contains(self, value):
        return value in self

    def exists(self, f: Callable[[A], bool]) -> bool:
        return self.find(f).is_just

    @property
    def is_empty(self):
        return self.length == 0

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
    def distinct(self):
        seen = set()
        return List.wrap(x for x in self if x not in seen and not seen.add(x))

    def __add__(self, other: typing.List[A]) -> 'List[A]':
        return List.wrap(typing.List.__add__(self, other))

    def without(self, el) -> 'List[A]':
        return self.filter(_ != el)

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
        return self.index_where(_ == target)

    @property
    def reversed(self):
        return List.wrap(reversed(self))

    def join(self, sep=''):
        return sep.join(self / str)

    def cons(self, item):
        return List.wrap(cons(item, self))

    def zip(self, other: 'Iterable[B]'):
        return List.wrap(zip(self, other))

    __and__ = zip


class ListMonad(Monad):

    def pure(self, b: B) -> List[B]:
        return List(b)

    def flat_map(self, fa: List[A], f: Callable[[A], List[B]]) -> List[B]:
        return List.wrap(flatten(map(f, fa)))


class ListTraverse(Traverse):

    @tc_prop
    def with_index(self, fa: List[A]) -> List[Tuple[int, A]]:
        return List.wrap(enumerate(fa))

    def filter(self, fa: List[A], f: Callable[[A], bool]):
        return List.wrap(filter(f, fa))

    @curried
    def fold_left(self, fa: List[A], z: B, f: Callable[[B, A], B]) -> B:
        return reduce(f, fa, z)

    def find_map(self, fa: List[A], f: Callable[[A], maybe.Maybe[B]]
                 ) -> maybe.Maybe[B]:
        for el in fa:
            found = f(el)
            if found.is_just:
                return found
        return maybe.Empty()

    def index_where(self, fa: List[A], f: Callable[[A], bool]):
        gen = (maybe.Just(i) for i, a in enumerate(fa) if f(a))
        return next(gen, maybe.Empty())  # type: ignore

__all__ = ('List',)
