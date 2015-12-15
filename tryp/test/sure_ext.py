from pathlib import Path

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
            assert isinstance(self.obj, Empty) or self.obj._get != what,\
                msg.format(self.obj, self.obj._get, what)
        else:
            self.be.a(Just)
            self.obj._get.should.equal(what)
        return True

    def _bool(self, pred, agent, action):
        no = ('not ' if self.negative else '') + 'to '
        assert pred(self.obj) ^ self.negative,\
            'expected {} \'{}\' {} {}'.format(agent, self.obj, no, action)
        return True

    @sure.assertionproperty
    def exist(self):
        err = "can only check existence of Path, not {}"
        assert isinstance(self.obj, Path), err.format(self.obj)
        return self._bool(lambda a: a.exists(), "path", "exist")


def install_assertion_builder(builder):
    sure.AssertionBuilder = builder

__all__ = ('install_assertion_builder', 'AssBuilder')
