from tryp import maybe


class Boolean(object):

    def __init__(self, value: bool) -> None:
        self.value = bool(value)

    @staticmethod
    def wrap(value):
        return Boolean(value)

    def maybe(self, value):
        return maybe.Maybe(value) if self else maybe.Empty()

    def flat_maybe(self, value: 'Maybe'):  # type: ignore
        return value if self else maybe.Empty()

    def maybe_call(self, f):
        return maybe.Just(f()) if self else maybe.Empty()

    def flat_maybe_call(self, f):
        return f() if self else maybe.Empty()

    def either(self, l, r) -> 'Either':  # type: ignore
        from tryp import Right, Left
        return Right(r) if self else Left(l)

    def __nonzero__(self):
        return self.value

    def __bool__(self):
        return self.value

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)

    __repr__ = __str__

    @property
    def no(self):
        return Boolean(not self.value)

__all__ = ('Boolean',)
