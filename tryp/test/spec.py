import tek  # type: ignore

import tryp
from tryp.logging import tryp_stdout_logging
import tryp.test.sure_ext


class Spec(tek.Spec):

    def setup(self, *a, **kw):
        tryp.development = True
        tryp_stdout_logging()
        super(Spec, self).setup(*a, **kw)

__all__ = ('Spec')
