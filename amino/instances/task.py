from typing import Callable, TypeVar, Type

from amino import Just, L, _, Nothing, Eval, Map
from amino.tc.monad import Monad
from amino.tc.base import ImplicitInstances, TypeClass
from amino.lazy import lazy
from amino.task import Task
from amino.util.fun import lambda_str

A = TypeVar('A')
B = TypeVar('B')


class TaskInstances(ImplicitInstances):

    @lazy
    def _instances(self) -> Map[Type[TypeClass], TypeClass]:
        from amino.map import Map
        return Map({Monad: TaskMonad()})


class TaskMonad(Monad[Task]):

    def pure(self, a: A) -> Task[A]:
        return Task.now(a)

    def flat_map(self, fa: Task[A], f: Callable[[A], Task[B]]) -> Task[B]:
        return fa.flat_map(f)

    def map(self, fa: Task[A], f: Callable[[A], B]) -> Task[B]:
        s = Eval.later(lambda: f'map({lambda_str(f)})')
        mapper = L(f)(_) >> L(Task.now)(_)
        return fa.flat_map(mapper, Nothing, Just(s))

__all__ = ('TaskInstances',)
