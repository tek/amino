import abc
from typing import Any

from amino import __, Just, List, I, Try, Maybe
from amino.anon.debug import AnonError
from amino.logging import amino_root_logger
from amino.list import Lists
from amino.test.spec_spec import Spec
from amino.test.spec import timed
from amino.anon.prod import __ as prod__, _ as prod_, L as prodL
from amino.anon.debug import __ as debug__, _ as debug_, L as debugL


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


class _Chain:

    def __init__(self, v) -> None:
        self.v = v

    def ma(self, a, b):
        return _Chain(self.v * a + b)

    def mb(self, a, b, c, d):
        return self.v * (a + b + c + d)


class _AnonSpec(Spec, abc.ABC):

    @abc.abstractproperty
    def __(self) -> Any:
        ...

    @abc.abstractproperty
    def _(self) -> Any:
        ...

    @abc.abstractproperty
    def L(self) -> Any:
        ...

    def _nested(self) -> None:
        z = 5
        a = 3
        b = 4
        o = _Outer()
        f = self.__.inner(z).wrap.add(a, b)
        f(o).should.equal(2 * z + a + b)

    def _complex(self) -> None:
        def f(a: int, b: int) -> int:
            return a + b
        l = self.L(f)(3, 4)
        l().should.equal(7)

    def _chain_complex(self) -> None:
        def f(i: int) -> Maybe[int]:
            return Just(i)
        l = self.L(f)(self._).map(lambda a: a + 1).map(lambda a: a + 2)
        l(6).should.equal(Just(9))

    def _complex_placeholders(self):
        v1 = 13
        v2 = 29
        def f(a, b, c, d):
            return b * d
        Just((v1, v2)).map2(self.L(f)(2, self._, 4, self._)).should.contain(v1 * v2)

    def _lambda_arg(self):
        v1 = _Num(13)
        v2 = 29
        v3 = 47
        v4 = 83
        f = lambda a, b, c, d: b * d
        l = self.L(f)(2, self.__.plus(v3), 4, self._ + v4)
        l(v1, v2).should.equal((v1.a + v3) * (v2 + v4))

    def _attr_lambda(self):
        a = _Att()
        l = self._.att.att
        l(a).should.equal(a)
        l2 = self._ + 6
        l2(3).should.equal(9)
        (6 - self._ + 3)(2).should.equal(7)
        (6 - self._ + 3 - 2 + 13)(2).should.equal(18)

    def _attr_lambda_2(self):
        (self._ % 3 == 2)(5).should.equal(True)
        (9 / self._)(3).should.equal(3.0)

    def _call_root(self):
        x = 5
        y = 4
        f = lambda a: a + y
        l = __(x)
        l(f).should.equal(x + y)

    def _getitem(self):
        f = __[1]
        a = 13
        f((1, a, 2)).should.equal(a)
        g = self.__.filter(self._ > 1)[1]
        b = 6
        g(List(4, 1, b)).should.equal(b)
        h = self._.x[0]
        h(Just(List(a))).should.equal(a)
        i = self._.x[0].length
        l = 3
        i(Just(List(Lists.range(3)))).should.equal(l)

    def _instantiate_type(self):
        a, b, c = 1, 2, 3
        class T:
            def __init__(self, a) -> None:
                self.a = a
            def __call__(self, a, b):
                return self.a, a, b
        l = Just(T) / __(a)
        (l / __(b, c)).should.contain((a, b, c))

    def _chain_method_lambda(self) -> None:
        v1, v2, v3, v4, v5, v6 = 2, 3, 5, 7, 11, 13
        a = _Chain(v3)
        f = __.ma(v4, v1).mb(v2, v5, v3, v6)
        target = (v3 * v4 + v1) * (v2 + v5 + v3 + v6)
        f(a).should.equal(target)

    def _method_lambda_with_placeholders(self):
        v1, v2, v3, v4, v5, v6 = 2, 3, 5, 7, 11, 13
        f = self.__.ma(self._, v1).mb(v2, self._, v3, self._)
        a = _Chain(v3)
        target = (v3 * v4 + v1) * (v2 + v5 + v3 + v6)
        f(a, v4, v5, v6).should.equal(target)

    def _lambda_arg_method_ref(self):
        values = List.range(5) / str
        s = values.mk_string(',')
        l = self.L(Try)(self.__.split, ',')
        (l(s) / List.wrap).should.contain(values)

    def _bad_param_count(self):
        f = self.__.map(self._).map(self._)
        args = List(1), lambda a: a, lambda a: a, 5
        f.when.called_with(*args).should.throw(AnonError)

    def _shift(self):
        f = self._ + 1
        g = self._ + 2
        l = self.L(f)(1) >> self.L(g)(self._)
        l().should.equal(4)

    def _nest_method_lambda_shift(self):
        class A(object):
            def run(self):
                pass
        l = self.L(self.__.run())(self._) >> self.L(I)(self._)
        l(A()).should.be.none

    def _lazy_method(self):
        values = List.range(5) / str
        s = values.mk_string(',')
        self.L(s).split(',')().should.equal(values)

    def _lazy_method_nested(self):
        class A:
            def __init__(self, a) -> None:
                self.a = a
        values = List.range(5) / str
        s = values.mk_string(',')
        a = A(A(A(s)))
        self.L(a).a.a.a.split(',')().should.equal(values)
        self.L(A)(self._).a.a.a.split(',')(A(A(s))).should.equal(values)

    def _nested_operator(self) -> None:
        f = self._.x + 'aaa'
        f(Just('bbb')).should.equal('bbbaaa')
        g = 'aaa' + self._.x
        g(Just('bbb')).should.equal('aaabbb')


class AnonDebugSpec(_AnonSpec):

    @property
    def __(self) -> Any:
        return debug__

    @property
    def _(self) -> Any:
        return debug_

    @property
    def L(self) -> Any:
        return debugL

    def nested(self):
        self._nested()

    def complex(self):
        self._complex()

    def chain_complex(self):
        self._chain_complex()

    def complex_placeholders(self):
        self._complex_placeholders()

    def lambda_arg(self):
        self._lambda_arg()

    def attr_lambda(self):
        self._attr_lambda()

    def attr_lambda_2(self):
        self._attr_lambda_2()

    def call_root(self):
        self._call_root()

    def getitem(self):
        self._getitem()

    def instantiate_type(self):
        self._instantiate_type()

    def method_lambda_with_placeholders(self):
        self._method_lambda_with_placeholders()

    def chain_method_lambda(self):
        self._chain_method_lambda()

    def lambda_arg_method_ref(self):
        self._lambda_arg_method_ref()

    def bad_param_count(self):
        self._bad_param_count()

    def shift(self):
        self._shift()

    def nest_method_lambda_shift(self):
        self._nest_method_lambda_shift()

    def lazy_method(self):
        self._lazy_method()

    def lazy_method_nested(self):
        self._lazy_method_nested()

    def nested_operator(self):
        self._nested_operator()


class AnonProdSpec(_AnonSpec):

    @property
    def __(self) -> Any:
        return prod__

    @property
    def _(self) -> Any:
        return prod_

    @property
    def L(self) -> Any:
        return prodL

    def nested(self):
        self._nested()

    def complex(self):
        self._complex()

    def chain_complex(self):
        self._chain_complex()

    def complex_placeholders(self):
        self._complex_placeholders()

    def lambda_arg(self):
        self._lambda_arg()

    def attr_lambda(self):
        self._attr_lambda()

    def attr_lambda_2(self):
        self._attr_lambda_2()

    def call_root(self):
        self._call_root()

    def getitem(self):
        self._getitem()

    def instantiate_type(self):
        self._instantiate_type()

    def chain_method_lambda(self):
        self._chain_method_lambda()

    def lambda_arg_method_ref(self):
        self._lambda_arg_method_ref()

    def shift(self):
        self._shift()

    def nest_method_lambda_shift(self):
        self._nest_method_lambda_shift()

    def lazy_method(self):
        self._lazy_method()

    def lazy_method_nested(self):
        self._lazy_method_nested()

    def nested_operator(self):
        self._nested_operator()


class _B:

    def __init__(self, b: int) -> None:
        self.b = b

    def get(self) -> int:
        return self.b

    def add(self, n: int) -> int:
        return self.b + n


class _A:

    def __init__(self, a: int) -> None:
        self.a = _B(a)

nums = Lists.wrap(_A(i) for i in range(10000))


class _BenchSpec(Spec):

    def _for_lambda_bench(self) -> None:
        amino_root_logger.info('')
        @timed
        def for_lambda() -> None:
            [a.a.get() for a in nums]
        for_lambda()

    def _run_method_lambda_bench(self, __: Any) -> None:
        @timed
        def map_method_lambda() -> None:
            nums.map(__.a.get())
        @timed
        def map_lambda() -> None:
            nums.map(lambda a: a.a.get())
        @timed
        def for_method_lambda() -> None:
            [__.a.get()(a) for a in nums]
        map_method_lambda()
        map_lambda()
        for_method_lambda()

    def method_lambda(self) -> None:
        f = prod__.a.add(5)
        f(_A(1)).should.equal(6)

    def _method_lambda_bench(self) -> None:
        self._for_lambda_bench()
        amino_root_logger.info('')
        amino_root_logger.info('debug:')
        self._run_method_lambda_bench(debug__)
        amino_root_logger.info('')
        amino_root_logger.info('prod:')
        self._run_method_lambda_bench(prod__)

__all__ = ('AnonDebugSpec', 'AnonProdSpec')
