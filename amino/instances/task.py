from typing import Callable, TypeVar
from types import FunctionType, MethodType

from amino import Just
from amino.tc.monad import Monad
from amino.tc.base import ImplicitInstances
from amino.lazy import lazy
from amino.task import Task

A = TypeVar('A')
B = TypeVar('B')


def lambda_str(f):
    if isinstance(f, MethodType):
        return '{}.{}'.format(f.__self__.__class__.__name__, f.__name__)
    elif isinstance(f, FunctionType):
        return f.__name__
    else:
        return repr(f)


class TaskInstances(ImplicitInstances):

    @lazy
    def _instances(self):
        from amino.map import Map
        return Map({Monad: TaskMonad()})


class TaskMonad(Monad):

    def pure(self, a: A):
        return Task(lambda: a, as_string=Just(a))

    def flat_map(self, fa: Task[A], f: Callable[[A], Task[B]]) -> Task[B]:
        s = '{}.flat_map({})'.format(fa.as_string, lambda_str(f))
        return Task(lambda: f(fa.run()).run(), 5, Just(s))

    def map(self, fa: Task[A], f: Callable[[A], B]) -> Task[B]:
        s = '{}.map({})'.format(fa.as_string, lambda_str(f))
        return Task(lambda: f(fa.run()), 5, Just(s))


__all__ = ('TaskInstances',)
