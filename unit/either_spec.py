from fn import _  # type: ignore

from tryp.either import Left, Right  # type: ignore
from tryp import Empty  # type: ignore
from tryp.test import Spec  # type: ignore


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
        Right(a).to_maybe.should.just_contain(a)
        Left(a).to_maybe.should.be.a(Empty)

__all__ = ['Either_']
