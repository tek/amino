from typing import Iterable, TypeVar, Any

from lenses.ui import UnboundLens
from lenses.optics import TrivialIso
from lenses.hooks.hook_funcs import from_iter

from amino import List, Lists


class UnboundLensA(UnboundLens):

    def __getattr__(self, name):
        # type: (str) -> Any
        if name.startswith('__') and name.endswith('__') or name.startswith('call_mut_') or name.startswith('call_'):
            return super().__getattr__(name)
        else:
            return self.GetAttr(name)


lens = UnboundLensA(TrivialIso())

A = TypeVar('A')


def list_from_iter(self, iterable: Iterable[A]) -> List[A]:
    return Lists.wrap(iterable)


from_iter.register(list)(list_from_iter)

__all__ = ('lens',)
