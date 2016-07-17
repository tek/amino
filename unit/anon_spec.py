from tryp import __, Just, _
from tryp.test import Spec
from tryp.anon import L


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

    def complex(self):
        v1 = 13
        v2 = 29
        def f(a, b, c, d):
            return b * d
        Just((v1, v2)).map2(L(f)(2, _, 4, _)).should.contain(v1 * v2)

__all__ = ('AnonSpec',)
