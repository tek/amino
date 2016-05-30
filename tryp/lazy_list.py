from functools import wraps
from typing import Generic, TypeVar, Callable, Tuple

from toolz import concatv

from tryp import _, Maybe
from tryp.list import List
from tryp.func import F, curried
from tryp.anon import __
from tryp.maybe import Just, Empty
from tryp.tc.functor import Functor
from tryp.tc.base import ImplicitInstances, Implicits, tc_prop
from tryp.lazy import lazy
from tryp.tc.traverse import Traverse

A = TypeVar('A')
B = TypeVar('B')


class LazyListInstances(ImplicitInstances):

    @lazy
    def _instances(self):
        from tryp.map import Map
        return Map({Functor: LazyListFunctor(), Traverse: LazyListTraverse()})


class LazyList(Generic[A], Implicits, implicits=True):
    _default_chunk_size = 20

    def fetch(f):
        @wraps(f)
        def wrapper(self, index):
            self._fetch(index)
            return f(self, index)
        return wrapper

    def __init__(self, source, init=List(), chunk_size=None,
                 post=lambda a: a) -> None:
        self.source = iter(source)
        self.strict = init
        self._chunk_size = chunk_size or self._default_chunk_size
        self._post = post

    @fetch
    def __getitem__(self, index):
        return self.strict.__getitem__(index)

    def __len__(self):
        return self.drain.length

    @property
    def _one(self):
        try:
            yield next(self.source)
        except StopIteration:
            pass

    def _fetch(self, index):
        count = index.stop if isinstance(index, slice) else index + 1
        def chunk():
            for i in range(self._chunk_size):
                yield from self._one
        def gen():
            while True:
                if self.strict.length < count:
                    c = list(chunk())
                    self.strict = self.strict + c
                    if len(c) == self._chunk_size:
                        continue
                break
        gen()

    @property
    def drain(self):
        self._fetch(float('inf'))
        return self.strict

    def copy(self, wrap_source, transstrict: Callable[[List[A]], List[A]]):
        return LazyList(wrap_source(self.source), transstrict(self.strict),
                        self._chunk_size, self._post)

    @fetch
    def lift(self, index):
        return self.strict.lift(index)

    @property
    def head(self):
        return self.lift(0)

    def _drain_find(self, abort):
        culprit = Empty()
        def gen():
            nonlocal culprit
            while True:
                try:
                    el = next(self.source)
                    yield el
                    if abort(el):
                        culprit = Just(el)
                        break
                except StopIteration:
                    break
        drained = List.wrap(list(gen()))
        self.strict = self.strict + drained
        return culprit

    def find(self, f: Callable[[A], bool]):
        return self.strict.find(f) | self._drain_find(f)

    def foreach(self, f):
        self.drain.foreach(f)

    @fetch
    def min_length(self, index):
        return self.strict.length >= index

    @fetch
    def max_length(self, index):
        return self.strict.length <= index

    @property
    def empty(self):
        return self.max_length(0)

    def append(self, other: 'LazyList[A]'):
        return self.copy(lambda s: concatv(s, other.source), lambda s: s +
                         other.strict)

    __add__ = append


class LazyListFunctor(Functor):

    def pure(self, a: A):
        return LazyList([], List(a))

    def map(self, fa: LazyList[A], f: Callable[[A], B]) -> LazyList[B]:
        return LazyList(map(f, fa.source), fa.strict, fa._chunk_size)


class LazyListTraverse(Traverse):

    @tc_prop
    def with_index(self, fa: LazyList[A]) -> List[Tuple[int, A]]:
        return LazyList(enumerate(fa.source), fa.strict, fa._chunk_size)

    def filter(self, fa: LazyList[A], f: Callable[[A], bool]):
        return fa.copy(F(filter, f), __.filter(f))

    @curried
    def fold_left(self, fa: LazyList[A], z: B, f: Callable[[B, A], B]) -> B:
        return Traverse[List].fold_left(fa.drain, z, f)

    def find_map(self, fa: LazyList[A], f: Callable[[A], Maybe[B]]
                 ) -> Maybe[B]:
        return fa.map(f).find(_.is_just)

    def index_where(self, fa: LazyList[A], f: Callable[[A], bool]
                    ) -> Maybe[int]:
        return fa.strict.index_where(f) | (
            fa._drain_find(f) / (lambda a: len(fa.strict) - 1))


def lazy_list(f):
    @wraps(f)
    def w(*a, **kw):
        return LazyList(f(*a, **kw))
    return w


def lazy_list_prop(f):
    return property(lazy_list(f))

__all__ = ('LazyList', 'lazy_list')
