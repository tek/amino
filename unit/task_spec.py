from amino.task import Task, TaskException
from amino.test import Spec
from amino import List, Right, L, _, Just, __


class TaskSpec(Spec):

    def sequence(self):
        f = lambda: 3
        t = List(Task.now(1), Task.now(2), Task.delay(f)).sequence(Task)
        t.attempt.should.equal(Right(List(1, 2, 3)))

    def zip(self):
        t = Task.now(1) & Task.now(2)
        t.attempt.should.equal(Right((1, 2)))

    def trampoline(self):
        t = (List.range(1000).fold_left(Task.now(1))(
            lambda z, a: z.flat_map(Task.now, fs=Just('now'))))
        t.attempt.should.contain(1)

    def now(self):
        v = 5
        t = Task.now(v)
        t.attempt.should.contain(v)

    def delay(self):
        v = 13
        w = 29
        f = _ + v
        t = Task.delay(f, w)
        t.run().should.equal(v + w)

    def suspend(self):
        v = 13
        w = 29
        f = lambda a: Task.now(a + v)
        t = Task.suspend(f, w)
        t.run().should.equal(v + w)

    def flat_map_now(self):
        v = 13
        w = 29
        t = Task.now(v).flat_map(L(Task.now)(_ + w))
        t.attempt.should.contain(v + w)

    def flat_map_delay(self):
        v = 13
        w = 29
        x = 17
        f = _ + x
        t = Task.delay(f, v).flat_map(L(Task.now)(_ + w))
        t.attempt.should.contain(v + w + x)

    def flat_map_delay_2(self):
        v = 13
        w = 29
        x = 17
        f = _ + w
        g = _ + x
        t = Task.delay(f, v).flat_map(lambda a: Task.delay(g, a))
        t.attempt.should.contain(v + w + x)

    def flat_map_twice(self):
        v = 13
        w = 29
        x = 17
        t = (
            Task.now(v)
            .flat_map(L(Task.now)(_ + w))
            .flat_map(L(Task.now)(_ + x))
        )
        t.attempt.should.contain(v + w + x)

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
        t.attempt.should.contain(v + w + x + y)

    def map(self):
        v = 13
        w = 29
        t = Task.now(v).map(_ + w)
        t.attempt.should.contain(v + w)

    def and_then(self):
        v = 7
        f = lambda: v
        t = Task.now(1).and_then(Task.delay(f))
        t.attempt.should.contain(v)

    def location(self):
        Task.debug = True
        TaskException.remove_pkgs = List('fn')
        def fail(a):
            raise Exception(str(a))
        f = lambda a: a + 2
        g = lambda a, b: Task.now(a + b)
        t = Task.delay(f, 1).flat_map(L(g)(_, 3))
        t2 = t.map(fail)
        exc = t2.attempt.value
        code = (exc.location / _.code_context) | ''
        code[0].should.contain('t.map(fail)')


class TaskStringSpec(Spec):

    def now(self):
        str(Task.now(5)).should.equal('Now(5)')

    def now_flat_map(self):
        t = Task.now(5) // Task.now
        target = 'Suspend(Now(5).flat_map(now))'
        str(t).should.equal(target)

    def suspend_flat_map(self):
        t = Task.suspend(Task.now, 5) // Task.now
        target = 'BindSuspend(now(5).flat_map(now))'
        str(t).should.equal(target)

    def now_map(self):
        t = Task.now(5) / (_ + 1)
        target = 'Suspend(Now(5).map((_ + 1)))'
        str(t).should.equal(target)
        str(t.step()).should.equal('Now(6)')

    def suspend_map(self):
        t = Task.suspend(Task.now, 5) / (_ + 1)
        target = 'Suspend(Now(5).map((_ + 1)))'
        str(t.step()).should.equal(target)

__all__ = ('TaskSpec', 'TaskStringSpec')
