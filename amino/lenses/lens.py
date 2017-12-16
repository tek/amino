from lenses.ui import UnboundLens
from lenses.optics import TrivialIso


class UnboundLensA(UnboundLens):

    def __getattr__(self, name):
        # type: (str) -> Any
        if name.startswith('__') and name.endswith('__') or name.startswith('call_mut_') or name.startswith('call_'):
            return super().__getattr__(name)
        else:
            return self.GetAttr(name)


lens = UnboundLensA(TrivialIso())

__all__ = ('lens',)
