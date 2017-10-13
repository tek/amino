from amino.dat import Dat
from amino.test.spec_spec import Spec


class V:
    pass


class CC(Dat['CC']):

    def __init__(self, a: V, b: str='asdf', c: int=6) -> None:
        self.a = a
        self.b = b
        self.c = c


class DatSpec(Spec):

    def test(self) -> None:
        c = CC(V(), 'aasf')
        c1: CC = c.copy(b='foo')
        c1.b.should.equal('foo')
        c2 = c1.set.c(7)
        c2.c.should.equal(7)

__all__ = ('DatSpec',)
