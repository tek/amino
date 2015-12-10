import sure  # NOQA
from flexmock import flexmock  # NOQA

from tek import Spec  # type: ignore

from tryp.lazy import lazy


class Test(object):
    i = 0

    @lazy
    def test(self) -> int:
        Test.i += 1
        return Test.i


class Lazy_(Spec):

    def lazy(self):
        t = Test()
        Test.i.should.equal(0)
        t.test.should.equal(1)
        t.test.should.equal(1)
        Test.i.should.equal(1)

__all__ = ['Lazy_']
