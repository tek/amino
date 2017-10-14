from amino.dat import Dat
from amino.test.spec_spec import Spec

from lenses import lens


class V(Dat['V']):

    def __init__(self, a: int, b: str) -> None:
        self.a = a
        self.b = b


class CC(Dat['CC']):

    def __init__(self, v: V, b: str='asdf', c: int=6) -> None:
        self.v = v
        self.b = b
        self.c = c


c1 = CC(V(1, 'v'), 'cc')
c2 = CC(V(2, 'v'), 'cc')


class DatSpec(Spec):

    def copy(self) -> None:
        c3: CC = c1.copy(b='foo')
        c3.b.should.equal('foo')
        c4 = c3.set.c(7)
        c4.c.should.equal(7)

    def eq(self) -> None:
        c1.should.equal(CC(V(1, 'v'), 'cc'))
        c1.should_not.equal(c2)
        (c1 == c2).should_not.be.ok

    def lens(self) -> None:
        lens(c1).v.a.set(2).should.equal(c2)

__all__ = ('DatSpec',)
