from fn import _

from tryp.test import Spec

from tryp import Maybe, Empty, Just, F, Left, Right
from tryp.tc.monad import Monad


class Maybe_(Spec):

    def none(self):
        Maybe(None).is_just.should_not.be.ok

    def just(self):
        Maybe('value').is_just.should.be.ok

    def map(self):
        a = 'start'
        b = 'end'
        Maybe(a).map(_ + b)._get.should.equal(a + b)
        (Maybe(a) / (_ + b))._get.should.equal(a + b)

    def flat_map(self):
        a = 'start'
        b = 'end'
        Maybe(a).flat_map(lambda v: Maybe(v + b)).should.contain(a + b)
        f = F(Maybe) // (_ + b) >> Monad[Maybe].pure  # type: ignore
        f(a).should.contain(a + b)

    def join(self):
        Just(Just(1)).join.should.equal(Just(1))

    def contains(self):
        a = 'start'
        Maybe(a).contains(a).should.be.ok
        Maybe(a + a).contains(a).should_not.be.ok
        Empty().contains(a).should_not.be.ok

    def get_or_else(self):
        e = Empty()
        a = 1
        e.get_or_else(a).should.equal(a)
        (e | a).should.equal(a)

    def get_or_else_call(self):
        e = Empty()
        a = 5
        ac = lambda: a
        e.get_or_else(ac).should.equal(a)
        (e | ac).should.equal(a)

    def or_else(self):
        e = Empty()
        a = Just(1)
        e.or_else(a).should.equal(a)

    def or_else_call(self):
        e = Empty()
        a = Just(5)
        ac = lambda: a
        e.or_else(ac).should.equal(a)

    def tap(self):
        a = 1
        b = 6

        def setter(c):
            nonlocal a
            a = c + 1
        (Just(b) % setter).should.contain(b)
        a.should.equal(b + 1)

    def ap2(self):
        a = 17
        b = 13
        ja = Just(a)
        jb = Just(b)
        ja.product(jb).smap(_ + _).should.contain(a + b)
        ja.ap2(jb, _ + _).should.contain(a + b)

    def optional(self):
        a = 'a'
        b = 'b'
        Maybe(a).to_maybe.should.just_contain(a)
        Empty().to_maybe.should.be.a(Empty)
        Maybe(a).to_either(b).should.equal(Right(a))
        Empty().to_either(b).should.equal(Left(b))
        Empty().to_either(lambda: b).should.equal(Left(b))

    def map_n(self):
        m = Just((1, 2, 3, 4))
        m.map4(lambda a, b, c, d: b + d).should.contain(6)
        m.map5.when.called_with(lambda a: a).should.throw(TypeError)

    def flat_map_n(self):
        m = Just((1, 2, 3, 4))
        m.flat_map4(lambda a, b, c, d: Just(b + d)).should.contain(6)
        m.flat_map5.when.called_with(lambda a: a).should.throw(TypeError)

    def product_n(self):
        m = Just(1).product3(Just(2), Just(3), Just(4))
        m.flat_map4(lambda a, b, c, d: Just(b + d)).should.contain(6)
        e = Just(1).product3(Just(2), Empty(), Just(4))
        e.should.be.empty

__all__ = ('Maybe_',)
