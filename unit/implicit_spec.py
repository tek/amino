from amino import Just
from amino.test import Spec
from amino.instances.maybe import MaybeMonad


class ImplicitSpec(Spec):

    def set_attr(self):
        Just(1).map.__wrapped__.__self__.should.be.a(MaybeMonad)

__all__ = ('ImplicitSpec',)
