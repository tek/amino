import sure  # NOQA
from flexmock import flexmock  # NOQA

from fn import _

from tek import Spec  # type: ignore

from tryp import Maybe, Empty


class Maybe_(Spec, ):

    def setup(self, *a, **kw):
        super(Maybe_, self).setup(*a, **kw)

    def none(self):
        Maybe(None).isJust.should_not.be.ok

    def just(self):
        Maybe('value').isJust.should.be.ok

    def map(self):
        a = 'start'
        b = 'end'
        Maybe(a).map(_ + b)._get.should.equal(a + b)

    def flatMap(self):
        a = 'start'
        b = 'end'
        Maybe(a).flatMap(lambda v: Maybe(v + b))._get.should.equal(a + b)

    def contains(self):
        a = 'start'
        Maybe(a).contains(a).should.be.ok
        Maybe(a + a).contains(a).should_not.be.ok
        Empty().contains(a).should_not.be.ok

__all__ = ['Maybe_']
