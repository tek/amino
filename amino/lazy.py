from typing import TypeVar, Generic, Callable, Union
import functools

A = TypeVar('A')
_attr_fmt = '_{}__value'


class LazyMeta(type):

    def __new__(mcs, name, bases, dct):
        lazies = [k for k, v in dct.items() if isinstance(v, lazy)]
        attrs = tuple(map('_{}__value'.format, lazies))
        inst = super().__new__(mcs, name, bases, dct)
        inst.__slots__ = attrs
        return inst


class LazyError(Exception):

    def __init__(self, name, inst):
        self.name = name
        self.inst = inst

    def __str__(self):
        msg = (
            'class {} with lazy attribute must have a __dict__,  a {}' +
            ' slot or use LazyMeta as metaclass'
        )
        return msg.format(type(self.inst).__name__, self.name)


class lazy(Generic[A]):

    def __init__(self, func: Callable[..., A], name=None) -> None:
        self.func = func
        self._attr_name = _attr_fmt.format(name or self.func.__name__)
        functools.wraps(self.func)(self)  # type: ignore

    def __get__(self, inst, inst_cls) -> Union[A, 'lazy[A]']:
        return self if inst is None else self._get(inst, inst_cls)

    def _get(self, inst, inst_cls):
        self._check(inst)
        return getattr(inst, self._attr_name)

    def _valid_slot(self, inst):
        return hasattr(inst, '__slots__') and self._attr_name in inst.__slots__

    def _check(self, inst):
        if not (hasattr(inst, '__dict__') or self._valid_slot):
            self._complain()
        if not hasattr(inst, self._attr_name):
            object.__setattr__(inst, self._attr_name, self.func(inst))

    def _complain(self, inst):
        raise LazyError(self._attr_name, inst)


class Lazy(metaclass=LazyMeta):
    pass

__all__ = ('lazy',)
