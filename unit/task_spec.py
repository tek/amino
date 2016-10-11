from amino.task import Task
from amino.test import Spec
from amino import List, Right, L, _


class TaskSpec(Spec):

    def sequence(self):
        f = lambda: 3
        t = List(Task.now(1), Task.now(2), Task.suspend(f)).sequence(Task)
        t.attempt().should.equal(Right(List(1, 2, 3)))

    def zip(self):
        t = Task.now(1) & Task.now(2)
        t.attempt().should.equal(Right((1, 2)))

    def trampoline(self):
        t = (List.range(1000).fold_left(Task.now(1))(
            lambda z, a: z.flat_map(Task.now)))
        t.attempt().should.contain(1)

    def now(self):
        v = 5
        t = Task.now(v)
        t.attempt().should.contain(v)

    def suspend(self):
        v = 13
        w = 29
        f = _ + v
        t = Task.suspend(f, w)
        t.attempt().should.contain(v + w)

    def flat_map_now(self):
        v = 13
        w = 29
        t = Task.now(v).flat_map(L(Task.now)(_ + w))
        t.attempt().should.contain(v + w)

    def flat_map_suspend(self):
        v = 13
        w = 29
        x = 17
        f = _ + x
        t = Task.suspend(f, v).flat_map(L(Task.now)(_ + w))
        t.attempt().should.contain(v + w + x)

    def flat_map_suspend_2(self):
        v = 13
        w = 29
        x = 17
        f = _ + w
        g = _ + x
        t = Task.suspend(f, v).flat_map(lambda a: Task.suspend(g, a))
        t.attempt().should.contain(v + w + x)

    def flat_map_twice(self):
        v = 13
        w = 29
        x = 17
        t = (
            Task.now(v)
            .flat_map(L(Task.now)(_ + w))
            .flat_map(L(Task.now)(_ + x))
        )
        t.attempt().should.contain(v + w + x)

    def flat_map_thrice(self):
        v = 13
        w = 29
        x = 17
        y = 11
        t = (
            Task.now(v)
            .flat_map(L(Task.now)(_ + w))
            .flat_map(L(Task.now)(_ + x))
            .flat_map(L(Task.now)(_ + y))
        )
        t.attempt().should.contain(v + w + x + y)

    def map(self):
        v = 13
        w = 29
        t = Task.now(v).map(_ + w)
        t.attempt().should.contain(v + w)

__all__ = ('TaskSpec',)
