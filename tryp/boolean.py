from tryp import maybe


class Boolean(object):

    def __init__(self, value: bool) -> None:
        self.value = bool(value)

    @staticmethod
    def wrap(value):
        return Boolean(value)

    def maybe(self, value):
        return maybe.Maybe(value) if self else maybe.Empty()

    def flat_maybe(self, value: 'maybe.Maybe'):
        return value if self else maybe.Empty()

    def __nonzero__(self):
        return self.value

    def __bool__(self):
        return self.value

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)

    __repr__ = __str__

__all__ = ['Boolean']
