from tryp.maybe import Empty, Maybe


class Boolean(object):

    def __init__(self, value: bool) -> None:
        self.value = value

    def maybe(self, value):
        return Maybe(value) if self else Empty()

    def flat_maybe(self, value: Maybe):
        return value if self else Empty()

    def __nonzero__(self):
        return self.value

__all__ = ['Boolean']
