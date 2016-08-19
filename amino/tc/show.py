from typing import TypeVar, Generic

A = TypeVar('A')


class Show(Generic[A]):

    def show(self, obj):
        return str(obj)

__all__ = ('Show',)
