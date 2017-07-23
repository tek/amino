from datetime import timedelta

from amino.test.spec_spec import Spec
from amino.tc.monoid import Monoid
from amino.instances.std.datetime import TimedeltaInstances  # NOQA
from amino import List


class TimedeltaSpec(Spec):

    def empty(self) -> None:
        Monoid.fatal(timedelta).empty.should.equal(timedelta(seconds=0))

    def combine(self) -> None:
        a = timedelta(seconds=5)
        b = timedelta(seconds=12)
        Monoid.fatal(timedelta).combine(a, b).should.equal(a + b)

    def fold(self) -> None:
        secs = List(4, 23, 45, 71)
        result = secs.map(lambda a: timedelta(seconds=a)).fold(timedelta)
        result.should.equal(timedelta(seconds=sum(secs)))

__all__ = ('TimedeltaSpec',)
