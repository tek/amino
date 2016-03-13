from tryp import __
from tryp.test import Spec  # type: ignore


class _Inner:

    def __init__(self, z) -> None:
        self.z = z

    @property
    def wrap(self):
        return _Inner(self.z * 2)

    def add(self, a, b):
        return self.z + a + b


class _Outer:

    def inner(self, z):
        return _Inner(z)


class AnonSpec(Spec):

    def nested(self):
        z = 5
        a = 3
        b = 4
        o = _Outer()
        f = __.inner(z).wrap.add(a, b)
        f(o).should.equal(2 * z + a + b)

__all__ = ('AnonSpec',)
