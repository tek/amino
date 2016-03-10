import sure  # NOQA
from flexmock import flexmock  # NOQA

from tryp import __
from tryp.test import Spec  # type: ignore


class Inner(object):

    def __init__(self, z) -> None:
        self.z = z

    def wrap(self, z):
        return Inner(self.z + z)

    def add(self, a, b):
        return self.z + a + b


class Outer(object):

    def inner(self, z):
        return Inner(z)


class AnonSpec(Spec):

    def nested(self):
        z = 5
        a = 3
        b = 4
        o = Outer()
        f = __.inner(z).wrap(z).add(a, b)
        f(o).should.equal(2 * z + a + b)

__all__ = ('AnonSpec',)
