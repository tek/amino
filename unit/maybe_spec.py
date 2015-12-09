import sure  # NOQA
from flexmock import flexmock  # NOQA

from fn import _

from tek import Spec  # type: ignore

from tryp import Maybe, Empty, Just


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

    def flat_map(self):
        a = 'start'
        b = 'end'
        Maybe(a).flat_map(lambda v: Maybe(v + b))._get.should.equal(a + b)

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

__all__ = ['Maybe_']
