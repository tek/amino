from amino.task import IO, IOException
from amino.test.spec_spec import Spec
from amino import List, Right, L, _, Just


class IOSpec(Spec):

    def sequence(self) -> None:
        f = lambda: 3
        t = List(IO.now(1), IO.now(2), IO.delay(f)).sequence(IO)
        t.attempt.should.equal(Right(List(1, 2, 3)))

    def zip(self) -> None:
        t = IO.now(1) & IO.now(2)
        t.attempt.should.equal(Right((1, 2)))

    def trampoline(self) -> None:
        t = (List.range(1000).fold_left(IO.now(1))(lambda z, a: z.flat_map(IO.now, fs=Just('now'))))
        t.attempt.should.contain(1)

    def now(self) -> None:
        v = 5
        t = IO.now(v)
        t.attempt.should.contain(v)

    def delay(self) -> None:
        v = 13
        w = 29
        f = _ + v
        t = IO.delay(f, w)
        t.run().should.equal(v + w)

    def suspend(self) -> None:
        v = 13
        w = 29
        f = lambda a: IO.now(a + v)
        t = IO.suspend(f, w)
        t.run().should.equal(v + w)

    def flat_map_now(self) -> None:
        v = 13
        w = 29
        t = IO.now(v).flat_map(L(IO.now)(_ + w))
        t.attempt.should.contain(v + w)

    def flat_map_delay(self) -> None:
        v = 13
        w = 29
        x = 17
        f = _ + x
        t = IO.delay(f, v).flat_map(L(IO.now)(_ + w))
        t.attempt.should.contain(v + w + x)

    def flat_map_delay_2(self) -> None:
        v = 13
        w = 29
        x = 17
        f = _ + w
        g = _ + x
        t = IO.delay(f, v).flat_map(lambda a: IO.delay(g, a))
        t.attempt.should.contain(v + w + x)

    def flat_map_twice(self) -> None:
        v = 13
        w = 29
        x = 17
        t = (
            IO.now(v)
            .flat_map(L(IO.now)(_ + w))
            .flat_map(L(IO.now)(_ + x))
        )
        t.attempt.should.contain(v + w + x)

    def flat_map_thrice(self) -> None:
        v = 13
        w = 29
        x = 17
        y = 11
        t = (
            IO.now(v)
            .flat_map(L(IO.now)(_ + w))
            .flat_map(L(IO.now)(_ + x))
            .flat_map(L(IO.now)(_ + y))
        )
        t.attempt.should.contain(v + w + x + y)

    def map(self) -> None:
        v = 13
        w = 29
        t = IO.now(v).map(_ + w)
        t.attempt.should.contain(v + w)

    def and_then(self) -> None:
        v = 7
        f = lambda: v
        t = IO.now(1).and_then(IO.delay(f))
        t.attempt.should.contain(v)

    def location(self) -> None:
        IO.debug = True
        IOException.remove_pkgs = List('fn')
        def fail(a: int) -> None:
            raise Exception(str(a))
        f = lambda a: a + 2
        g = lambda a, b: IO.now(a + b)
        t = IO.delay(f, 1).flat_map(L(g)(_, 3))
        t2 = t.map(fail)
        exc = t2._attempt().value
        code = (exc.location / _.code_context) | ''
        code[0].should.contain('t.map(fail)')


class IOStringSpec(Spec):

    def now(self) -> None:
        str(IO.now(5)).should.equal('Now(5)')

    def now_flat_map(self) -> None:
        t = IO.now(5) // IO.now
        target = 'Suspend(Now(5).flat_map(now))'
        str(t).should.equal(target)

    def suspend_flat_map(self) -> None:
        t = IO.suspend(IO.now, 5) // IO.now
        target = 'BindSuspend(now(5).flat_map(now))'
        str(t).should.equal(target)

    def now_map(self) -> None:
        t = IO.now(5) / (_ + 1)
        print(t.thunk().value)
        target = 'Suspend(Now(5).map(lambda a: (lambda b: a + b)(1)))'
        str(t).should.equal(target)
        str(t.step()).should.equal('Now(6)')

    def suspend_map(self) -> None:
        t = IO.suspend(IO.now, 5) / (_ + 1)
        target = 'Suspend(Now(5).map(lambda a: (lambda b: a + b)(1)))'
        str(t.step()).should.equal(target)

__all__ = ('IOSpec', 'IOStringSpec')
