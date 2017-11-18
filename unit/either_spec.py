import operator

from amino.either import Left, Right
from amino import Empty, Just, Maybe, List, Either, _
from amino.test.spec_spec import Spec
from amino.list import Lists


class EitherSpec(Spec):

    def map(self) -> None:
        a = 'a'
        b = 'b'
        Right(a).map(_ + b).value.should.equal(a + b)
        Left(a).map(_ + b).value.should.equal(a)

    def optional(self) -> None:
        a = 'a'
        b = 'b'
        Right(a).to_maybe.should.just_contain(a)
        Left(a).to_maybe.should.be.a(Empty)
        Right(a).to_either(b).should.equal(Right(a))
        Left(a).to_either(b).should.equal(Left(a))

    def ap2(self) -> None:
        a = 'a'
        b = 'b'
        Right(a).ap2(Right(b), operator.add).should.equal(Right(a + b))

    def traverse(self) -> None:
        a = 'a'
        Right(Just(a)).sequence(Maybe).should.equal(Just(Right(a)))
        Left(Just(a)).sequence(Maybe).should.equal(Just(Left(Just(a))))
        List(Right(a)).sequence(Either).should.equal(Right(List(a)))
        List(Right(a), Left(a)).sequence(Either).should.equal(Left(a))

    def fold_m(self) -> None:
        def f(z: int, a: int) -> Either[str, int]:
            return Right(z + a) if a < 5 else Left('too large')
        Lists.range(5).fold_m(Right(8))(f).should.contain(18)
        Lists.range(6).fold_m(Right(8))(f).should.be.left

    def list_flat_map(self) -> None:
        (List(Right(1), Left(2), Right(3)).join).should.equal(List(1, 3))

__all__ = ('EitherSpec',)
