from amino import ADT
from amino.case import CaseRec, Term
from amino.test.spec_spec import Spec


class Num(ADT['Num']):
    pass


class Int(Num):

    def __init__(self, i: int) -> None:
        self.i = i


class Float(Num):

    def __init__(self, f: float) -> None:
        self.f = f


class Prod(Num):

    def __init__(self, p: int) -> None:
        self.p = p


class rec(CaseRec[int, int], alg=Num):

    def __init__(self, base: int) -> None:
        self.base = base

    def int(self, n: Int) -> int:
        return self(Prod(self.base * n.i))

    def float(self, n: Float) -> int:
        return self(Int(int(n)))

    def prod(self, n: Prod) -> int:
        return Term(n.p + 7)


class CaseSpec(Spec):

    def test(self) -> None:
        r = rec(5)(Int(6)).eval()
        r.should.equal(37)


__all__ = ('CaseSpec',)
