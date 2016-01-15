import sure  # NOQA
from flexmock import flexmock  # NOQA

from tryp import __
from tryp.test import Spec


class Anon_(Spec):

    def setup(self, *a, **kw):
        super().setup(*a, **kw)

    def anon_call(self):
        class Adder(object):
            def add(self, a, b):
                return a + b
        adder = Adder()
        a = 3
        b = 4
        f = __.add(a, b)
        f(adder).should.equal(7)

__all__ = ('Anon_')
