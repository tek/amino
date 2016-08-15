from fn import _

from tryp.either import Left, Right
from tryp import Empty, Just, Maybe
from tryp.test import Spec


class EitherSpec(Spec):

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

    def ap2(self):
        a = 'a'
        b = 'b'
        Right(a).ap2(Right(b), _ + _).should.equal(Right(a + b))

    def traverse(self):
        a = 'a'
        Right(Just(a)).sequence(Maybe).should.equal(Just(Right(a)))
        Left(Just(a)).sequence(Maybe).should.equal(Just(Left(Just(a))))

__all__ = ('EitherSpec',)
