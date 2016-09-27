import itertools
from functools import wraps
from typing import Generic, TypeVar, Callable

from toolz import concatv

from amino.list import List
from amino.maybe import Just, Empty
from amino.tc.base import Implicits
from amino.func import I
from amino.util.string import safe_string

A = TypeVar('A')
B = TypeVar('B')


class LazyList(Generic[A], Implicits, implicits=True):
    _default_chunk_size = 20

    def fetch(f):
        @wraps(f)
        def wrapper(self, index):
            self._fetch(index)
            return f(self, index)
        return wrapper

    def __init__(self, source, init=List(), chunk_size=None, post=I) -> None:
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
    def drain(self) -> List[A]:
        self._fetch(float('inf'))
        return self.strict

    def copy(self, wrap_source, transstrict: Callable[[List[A]], List[A]]):
        a, b = itertools.tee(self.source)
        self.source = a
        return LazyList(wrap_source(b), transstrict(self.strict),
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

    def __repr__(self):
        strict = (self.strict / safe_string).mk_string(', ')
        return '{}({} {!r})'.format(self.__class__.__name__, strict,
                                    self.source)


def lazy_list(f):
    @wraps(f)
    def w(*a, **kw):
        return LazyList(f(*a, **kw))
    return w


def lazy_list_prop(f):
    return property(lazy_list(f))

__all__ = ('LazyList', 'lazy_list')
