import spec

from amino.test.spec import SpecBase, IntegrationSpecBase


class Spec(SpecBase, spec.Spec):
    pass


class IntegrationSpec(IntegrationSpecBase, Spec):
    pass

__all__ = ('Spec',)
