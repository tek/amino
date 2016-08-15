import sure  # NOQA
from flexmock import flexmock  # NOQA

from tryp.lazy import lazy, Lazy
from tryp.test import Spec


class A(Lazy):
    __slots__ = ['a']
    i = 0

    @lazy
    def test(self) -> int:
        A.i += 1
        return A.i


class B(object):
    i = 0

    @lazy
    def test(self) -> int:
        B.i += 1
        return B.i


class LazySpec(Spec):

    def _impl(self, tpe):
        t = tpe()
        t2 = tpe()
        tpe.i.should.equal(0)
        t.test.should.equal(1)
        t2.test.should.equal(2)
        t.test.should.equal(1)
        t.test.should.equal(1)
        t.test.should.equal(1)
        tpe.i.should.equal(2)

    def slots(self):
        self._impl(A)

    def dict(self):
        self._impl(B)

__all__ = ('LazySpec',)
