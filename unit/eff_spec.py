import random

from amino import List, Right, _, Just, Empty, Maybe, Either, Left

from amino.test.spec_spec import Spec
from amino.task import Task


class EffSpec(Spec):

    @property
    def _r(self):
        a, b = random.randint(0, 10), random.randint(0, 10)
        return (a, b) if a != b else self._r

    def eff_map(self):
        a, b = self._r
        c = -1
        t = Right(List(Just(Right(a)), Just(Left(c)), Empty()))
        target = Right(List(Just(Right(a + b)), Just(Left(c)), Empty()))
        res = t.effs(3).map(_ + b)
        res.value.should.equal(target)

    def eff_map_task(self):
        a, b = self._r
        t = Task.now(List(Just(a), Just(b), Empty()))
        target = List(Just(a + b), Just(b + b), Empty())
        res = t.effs(2).map(_ + b)
        res.value.run().should.equal(target)

    def eff_flat(self):
        a, b = self._r
        t = List(Just(Right(Just(a))))
        target = List(Just(Right(Just(a + b))))
        res = (t.effs(3, Maybe, Either, Maybe)
               .flat_map(lambda x: List(Just(Right(Just(x + b))))))
        res.value.should.equal(target)

    def eff_flat_empty(self):
        t = List(Right(Empty()))
        target = List(Right(Empty()))
        res = (t.effs(3, Either, Maybe, Maybe)
               .flat_map(lambda x: List(Right(Just(Just(1))))))
        res.value.should.equal(target)

    def eff_flat_task(self):
        a, b = self._r
        t = Task.now(List(Right(Just(Right(a)))))
        target = List(Right(Just(Right(a + b))))
        res = (t.effs(4, List, Either, Maybe, Either)
               .flat_map(lambda x: Task.now(List(Right(Just(Right(x + b)))))))
        res.value.run().should.equal(target)

    def eff_flat_task_empty(self):
        t = Task.now(List(Right(Empty())))
        target = List(Right(Empty()))
        res = (t.effs(4, List, Either, Maybe, Either)
               .flat_map(lambda x: Task.now(List(Right(Just(Right(1)))))))
        res.value.run().should.equal(target)

    def eff_flat_task_left(self):
        a, b = self._r
        t = Task.now(Left(Just(a)))
        target = Left(Just(a))
        res = t.effs(1, Either, Maybe) // (lambda x: Task.now(Right(Just(b))))
        res.value.run().should.equal(target)

__all__ = ('EffSpec',)
