from typing import Callable, TypeVar

from tryp import Just
from tryp.tc.monad import Monad
from tryp.tc.base import ImplicitInstances
from tryp.lazy import lazy
from tryp.task import Task

A = TypeVar('A')
B = TypeVar('B')


class TaskInstances(ImplicitInstances):

    @lazy
    def _instances(self):
        from tryp.map import Map
        return Map({Monad: TaskMonad()})


class TaskMonad(Monad):

    def pure(self, a: A):
        return Task(lambda: a, as_string=Just(a))

    def flat_map(self, fa: Task[A], f: Callable[[A], Task[B]]) -> Task[B]:
        s = '{}.flat_map({!r})'.format(fa.as_string, f)
        return Task(lambda: f(fa.run()).run(), 5, Just(s))

    def map(self, fa: Task[A], f: Callable[[A], B]) -> Task[B]:
        s = '{}.map({!r})'.format(fa.as_string, f)
        return Task(lambda: f(fa.run()), 5, Just(s))


__all__ = ('TaskInstances',)