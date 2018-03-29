from amino import ADT
from amino.case import CaseRec, Term
from amino.test.spec_spec import Spec


class _Num(ADT['_Num']):
    pass


class _Int(_Num):

    def __init__(self, i: int) -> None:
        self.i = i


class _Float(_Num):

    def __init__(self, f: float) -> None:
        self.f = f


class _Prod(_Num):

    def __init__(self, p: int) -> None:
        self.p = p


class _rec(CaseRec[int, int], alg=_Num):

    def __init__(self, base: int) -> None:
        self.base = base

    def _int(self, n: _Int) -> int:
        return self(_Prod(self.base * n.i))

    def _float(self, n: _Float) -> int:
        return self(_Int(int(n)))

    def _prod(self, n: _Prod) -> int:
        return Term(n.p + 7)


class CaseSpec(Spec):

    def _rec(self) -> None:
        r = _rec(5)(_Int(6)).eval()
        r.should.equal(37)


__all__ = ('CaseSpec',)
