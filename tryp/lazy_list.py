from functools import wraps
from typing import Generic, TypeVar, Callable, Tuple

from tryp import _
from tryp.list import List
from tryp.func import F
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
        self._strict = init
        self._chunk_size = chunk_size or self._default_chunk_size
        self._post = post

    @fetch
    def __getitem__(self, index):
        return self._strict.__getitem__(index)

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
        def go():
            if self._strict.length < count:
                c = list(chunk())
                self._strict = self._strict + c
                if len(c) == self._chunk_size:
                    go()
        go()

    @property
    def drain(self):
        self._fetch(float('inf'))
        return self._strict

    def copy(self, wrap_source, trans_strict: Callable[[List[A]], List[A]]):
        return LazyList(wrap_source(self.source), trans_strict(self._strict),
                        self._chunk_size, self._post)

    @fetch
    def lift(self, index):
        return self._strict.lift(index)

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
        drained = List.wrap(gen())
        self._strict = self._strict + drained
        return culprit

    def index_of(self, item):
        return self._strict.index_of(item) | (
            self._drain_find(_ == item) / (lambda a: len(self._strict) - 1))

    def find(self, item):
        return self._strict.find(_ == item) | self._drain_find(_ == item)

    def foreach(self, f):
        self.drain.foreach(f)

    @fetch
    def min_length(self, index):
        return self._strict.length >= index


class LazyListFunctor(Functor):

    def pure(self, a: A):
        return LazyList([], List(a))

    def map(self, fa: LazyList[A], f: Callable[[A], B]) -> LazyList[B]:
        return LazyList(map(f, fa.source), fa._strict, fa._chunk_size)


class LazyListTraverse(Traverse):

    @tc_prop
    def with_index(self, fa: LazyList[A]) -> List[Tuple[int, A]]:
        return LazyList(enumerate(fa.source), fa._strict, fa._chunk_size)

    def filter(self, fa: LazyList[A], f: Callable[[A], bool]):
        return fa.copy(F(filter, f), __.filter(f))

__all__ = ('LazyList',)
