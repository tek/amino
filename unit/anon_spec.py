from amino import __, Just, List, I, Try
from amino.test import Spec
from amino.anon import L, _, AnonError


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
        l = L(f)(2, __.plus(v3), 4, _ + v4)
        l(v1, v2).should.equal((v1.a + v3) * (v2 + v4))

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
        h = _.x[0]
        h(Just(List(a))).should.equal(a)

    def instantiate_type(self):
        a, b, c = 1, 2, 3
        class T:
            def __init__(self, a) -> None:
                self.a = a
            def __call__(self, a, b):
                return self.a, a, b
        l = Just(T) / __(a)
        (l / __(b, c)).should.contain((a, b, c))

    def method_lambda_with_placeholders(self):
        class A:
            def __init__(self, v) -> None:
                self.v = v
            def ma(self, a, b):
                return A(self.v * a + b)
            def mb(self, a, b, c, d):
                return self.v * (a + b + c + d)
        v1, v2, v3, v4, v5, v6 = 2, 3, 5, 7, 11, 13
        f = __.ma(_, v1).mb(v2, _, v3, _)
        a = A(v3)
        target = (v3 * v4 + v1) * (v2 + v5 + v3 + v6)
        f(a, v4, v5, v6).should.equal(target)

    def lambda_arg_method_ref(self):
        values = List.range(5) / str
        s = values.mk_string(',')
        l = L(Try)(__.split, ',')
        (l(s) / List.wrap).should.contain(values)

    def bad_param_count(self):
        f = __.map(_).map(_)
        args = List(1), lambda a: a, lambda a: a, 5
        f.when.called_with(*args).should.throw(AnonError)

    def shift(self):
        f = _ + 1
        g = _ + 2
        l = L(f)(1) >> L(g)(_)
        l().should.equal(4)

    def nest_method_lambda_shift(self):
        class A(object):
            def run(self):
                pass
        l = L(__.run())(_) >> L(I)(_)
        l(A()).should.be.none

    def lazy_method(self):
        values = List.range(5) / str
        s = values.mk_string(',')
        L(s).split(',')().should.equal(values)

    def lazy_method_nested(self):
        class A:
            def __init__(self, a) -> None:
                self.a = a
        values = List.range(5) / str
        s = values.mk_string(',')
        a = A(A(A(s)))
        L(a).a.a.a.split(',')().should.equal(values)

__all__ = ('AnonSpec',)
