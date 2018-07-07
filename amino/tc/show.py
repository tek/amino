from typing import TypeVar, Generic

from amino.tc.base import TypeClass

A = TypeVar('A')


class Show(TypeClass):

    def show(self, obj):
        return str(obj)

__all__ = ('Show',)
