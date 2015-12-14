import sure

from tryp import Maybe, Empty, Just


class AssBuilder(sure.AssertionBuilder):

    @sure.assertionmethod
    def contain(self, what):
        if isinstance(self.obj, Maybe):
            return self.just_contain(what)
        else:
            return super(AssBuilder, self).contain(what)

    @sure.assertionmethod
    def just_contain(self, what):
        self.obj.should.be.a(Maybe)
        if self.negative:
            msg = "{} contains {}, expected {}"
            assert(
                isinstance(self.obj, Empty) or self.obj._get != what,
                msg.format(self.obj, self.obj._get, what)
            )
        else:
            self.be.a(Just)
            self.obj._get.should.equal(what)
        return True

sure.AssertionBuilder = AssBuilder

__all__ = ()
