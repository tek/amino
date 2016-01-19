from tryp.maybe import Empty, Maybe


class Boolean(object):

    def __init__(self, value: bool) -> None:
        self.value = bool(value)

    @staticmethod
    def wrap(value):
        return Boolean(value)

    def maybe(self, value):
        return Maybe(value) if self else Empty()

    def flat_maybe(self, value: Maybe):
        return value if self else Empty()

    def __nonzero__(self):
        return self.value

    def __bool__(self):
        return self.value

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)

    __repr__ = __str__

__all__ = ['Boolean']
