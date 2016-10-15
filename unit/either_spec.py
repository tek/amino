import operator

from amino.either import Left, Right
from amino import Empty, Just, Maybe, List, Either, _
from amino.test import Spec


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
        Right(a).ap2(Right(b), operator.add).should.equal(Right(a + b))

    def traverse(self):
        a = 'a'
        Right(Just(a)).sequence(Maybe).should.equal(Just(Right(a)))
        Left(Just(a)).sequence(Maybe).should.equal(Just(Left(Just(a))))
        List(Right(a)).sequence(Either).should.equal(Right(List(a)))
        List(Right(a), Left(a)).sequence(Either).should.equal(Left(a))

__all__ = ('EitherSpec',)
