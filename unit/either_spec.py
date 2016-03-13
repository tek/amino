from fn import _

from tryp.either import Left, Right
from tryp import Empty, Just
from tryp.test import Spec


class Either_(Spec):

    def setup(self, *a, **kw):
        super(Either_, self).setup(*a, **kw)

    def map(self):
        a = 'a'
        b = 'b'
        Right(a).map(_ + b).value.should.equal(a + b)
        Left(a).map(_ + b).value.should.equal(a)

    def optional(self):
        a = 'a'
        b = 'b'
        Right(a).to_maybe.should.just_contain(a)
        Left(a).to_maybe.should.be.a(Empty)
        Right(a).to_either(b).should.equal(Right(a))
        Left(a).to_either(b).should.equal(Left(a))

    def map2(self):
        a = 'a'
        b = 'b'
        Right(a).map2(Right(b), _ + _).should.equal(Right(a + b))

__all__ = ['Either_']
