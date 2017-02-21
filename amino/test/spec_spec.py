import spec

from amino.test.spec import SpecBase, IntegrationSpecBase
from amino.test.sure import SureSpec


class Spec(SureSpec, SpecBase, spec.Spec):

    def setup(self) -> None:
        SureSpec.setup(self)
        SpecBase.setup(self)


class IntegrationSpec(IntegrationSpecBase, Spec):
    pass

__all__ = ('Spec',)
