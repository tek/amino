from amino.test.spec_spec import Spec
from amino.id import Id


class IdSpec(Spec):

    def monad(self) -> None:
        Id(5).flat_map(lambda a: Id(a + 6)).should.equal(Id(11))
        Id(8).map(lambda a: a / 2).should.equal(Id(4))

__all__ = ('IdSpec',)
