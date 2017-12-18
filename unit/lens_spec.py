from lenses import lens, bind

from amino import List, _
from amino.test.spec_spec import Spec
from amino.lenses.tree import path_lens_pred


class B:

    def __init__(self, a, b=1) -> None:
        self.a = a
        self.b = b

    def __repr__(self):
        return 'B({}, {})'.format(self.a, self.b)

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b


class A:

    def __init__(self, b: List[B]) -> None:
        self.b = b

    def __repr__(self):
        return 'A({!r})'.format(self.b)

    def __eq__(self, other):
        return self.b == other.b


class C:

    def __init__(self, a, c: List['C']=List()) -> None:
        self.a = a
        self.c = c

    def __repr__(self):
        sub = '' if self.c.is_empty else ', {!r}'.format(self.c)
        return 'C({}{})'.format(self.a, sub)

    def __eq__(self, other):
        return self.a == other.a and self.c == other.c


class LensSpec(Spec):

    def tuple_(self):
        x, y, z = 11, 22, 33
        def mod(a):
            a[0][1].a = B(y)
            return a[0], B(x), bind(a[2]).b.set(z)
        b = List(B(B(0)), B(B(1)), B(B(2)))
        a = A(b)
        l1 = lens.GetAttr('b')
        l2 = lens.GetAttr('b')[0].GetAttr('a')
        l3 = lens.GetAttr('b')[2]
        l = lens.Tuple(l1, l2, l3)
        target = A(List(B(B(x)), B(B(y)), B(B(2), z)))
        l.modify(mod)(a).should.equal(target)

    def path(self):
        c = C(1, List(C(2), C(3, List(C(4, List(C(5))), C(6))), C(7)))
        t = path_lens_pred(c, _.c, _.a, _ == 5).x
        mod = lambda a: (a + 10 if isinstance(a, int) else bind(a).a.modify(_ + 20))
        m = t.modify(lambda a: map(mod, a))
        target = C(21, List(C(2), C(23, List(C(24, List(C(15))), C(6))), C(7)))
        m.should.equal(target)
        m2 = t.get()
        t.set(map(mod, m2)).should.equal(target)

__all__ = ('LensSpec',)
