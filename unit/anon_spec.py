from amino import __, Just, List
from amino.test import Spec
from amino.anon import L, _


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


class _Num:

    def __init__(self, a) -> None:
        self.a = a

    def plus(self, fact):
        return self.a + fact


class _Att:

    @property
    def att(self):
        return self


class MyClass(object):
    pass


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

    def lambda_arg(self):
        v1 = _Num(13)
        v2 = 29
        v3 = 47
        v4 = 83
        f = lambda a, b, c, d: b * d
        res = Just((v1, v2)).map2(L(f)(2, __.plus(v3), 4, _ + v4))
        res.should.contain((v1.a + v3) * (v2 + v4))

    def attr_lambda(self):
        a = _Att()
        l = _.att.att
        l(a).should.equal(a)
        l2 = _ + 6
        l2(3).should.equal(9)
        (6 - _ + 3)(2).should.equal(7)

    def attr_lambda_2(self):
        (_ % 3 == 2)(5).should.equal(True)
        (9 / _)(3).should.equal(3.0)

    def call_root(self):
        x = 5
        y = 4
        f = lambda a: a + y
        l = __(x)
        l(f).should.equal(x + y)

    def getitem(self):
        f = __[1]
        a = 13
        f((1, a, 2)).should.equal(a)
        g = __.filter(_ > 1)[1]
        b = 6
        g(List(4, 1, b)).should.equal(b)

__all__ = ('AnonSpec',)
