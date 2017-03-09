import time
from datetime import datetime

import spec

from amino.test.spec import SpecBase, IntegrationSpecBase, default_timeout
from amino.test.sure import SureSpec


def later(ass, *a, timeout=None, intval=0.1, **kw):
    timeout = default_timeout if timeout is None else timeout
    start = datetime.now()
    ok = False
    while not ok and (datetime.now() - start).total_seconds() < timeout:
        try:
            ass(*a, **kw)
            ok = True
        except AssertionError:
            time.sleep(intval)
    return ass(*a, **kw)


class Spec(SureSpec, SpecBase, spec.Spec):

    def setup(self) -> None:
        SureSpec.setup(self)
        SpecBase.setup(self)

    def _wait_for(self, pred, timeout=default_timeout, intval=0.1):
        start = datetime.now()
        while (not pred() and
               (datetime.now() - start).total_seconds() < timeout):
            time.sleep(intval)
        pred().should.be.ok


class IntegrationSpec(IntegrationSpecBase, Spec):
    pass

__all__ = ('Spec',)
