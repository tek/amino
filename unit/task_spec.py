import random

from tryp.task import Task
from tryp.test import Spec
from tryp import List, Right, _, Just, Empty


class TaskSpec(Spec):

    def sequence(self):
        f = lambda: 3
        t = List(Task.now(1), Task.now(2), Task(f)).sequence(Task)
        t.unsafe_perform_sync().should.equal(Right(List(1, 2, 3)))

    def zip(self):
        t = Task.now(1) & Task.now(2)
        t.unsafe_perform_sync().should.equal(Right((1, 2)))

    def eff(self):
        a = random.randint(0, 10)
        b = random.randint(0, 10)
        t = Task.now(List(Just(a), Just(b), Empty()))
        target = Right(List(Just(a + b), Just(b + b), Empty()))
        res = t.effs(2).map(_ + b)
        res.value.unsafe_perform_sync().should.equal(target)

__all__ = ('TaskSpec',)
