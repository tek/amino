import abc

from tryp.tc.base import TypeClass
from tryp.tc.functor import F


class Monoidal(TypeClass):

    @abc.abstractmethod
    def product(self, fa: F, fb: F) -> F:
        ...

__all__ = ('Monoidal',)
