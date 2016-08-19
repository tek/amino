import abc

from amino.tc.base import TypeClass
from amino.tc.functor import F


class Monoidal(TypeClass):

    @abc.abstractmethod
    def product(self, fa: F, fb: F) -> F:
        ...

__all__ = ('Monoidal',)
