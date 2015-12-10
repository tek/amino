from typing import TypeVar, Generic, Callable, Union, Any
import functools

A = TypeVar('A')


class lazy(Generic[A]):

    def __init__(self, func: Callable[[Any], A]) -> None:
        self.func = func
        self._attr_name = '_{}__value'.format(self.func.__name__)
        functools.wraps(self.func)(self)

    def __get__(self, inst, inst_cls) -> Union[A, 'lazy[A]']:
        if inst is None:
            return self
        else:
            assert hasattr(inst, '__dict__')
            if not hasattr(inst, self._attr_name):
                setattr(inst, self._attr_name, self.func(inst))
            return getattr(inst, self._attr_name)

__all__ = ['lazy']
