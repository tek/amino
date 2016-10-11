from typing import Callable, TypeVar

from amino import Just
from amino.tc.monad import Monad
from amino.tc.base import ImplicitInstances
from amino.lazy import lazy
from amino.task import Task
from amino.anon import lambda_str

A = TypeVar('A')
B = TypeVar('B')


class TaskInstances(ImplicitInstances):

    @lazy
    def _instances(self):
        from amino.map import Map
        return Map({Monad: TaskMonad()})


class TaskMonad(Monad):

    def pure(self, a: A):
        return Task.now(a)

    def flat_map(self, fa: Task[A], f: Callable[[A], Task[B]]) -> Task[B]:
        return fa.flat_map(f)

    def map(self, fa: Task[A], f: Callable[[A], B]) -> Task[B]:
        s = '{}.map({})'.format(fa.as_string, lambda_str(f))
        def map(a):
            return Task.now(f(a))
        return fa.flat_map(map)


__all__ = ('TaskInstances',)
