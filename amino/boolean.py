from amino import maybe
from amino.either import Right, Left
from amino.func import call_by_name


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

    def maybe_call(self, f, *a, **kw):
        return maybe.Just(f(*a, **kw)) if self else maybe.Empty()

    def m(self, v):
        return maybe.Maybe(call_by_name(v)) if self else maybe.Empty()

    def flat_maybe_call(self, f, *a, **kw):
        return f(*a, **kw) if self else maybe.Empty()

    def either(self, l, r):
        return self.either_call(l, lambda: r)

    def either_call(self, l, r):
        return Right(r()) if self else Left(l)

    def flat_either_call(self, l, r):
        return r() if self else Left(l)

    def e(self, l, r):
        return Right(call_by_name(r)) if self else Left(call_by_name(l))

    def flat_e(self, l, r):
        return call_by_name(r) if self else Left(call_by_name(l))

    def cata(self, t, f):
        return t if self.value else f

    def cata_call(self, t, f):
        return t() if self.value else f()

    def c(self, t, f):
        return call_by_name(t) if self.value else call_by_name(f)

    def __nonzero__(self):
        return self.value

    def __bool__(self):
        return self.value

    def __str__(self):
        return '{}({})'.format(self.__class__.__name__, self.value)

    __repr__ = __str__

    def __eq__(self, other):
        return (
            self.value == other
            if isinstance(other, bool) else
            self.value == other.value
            if isinstance(other, Boolean) else
            False
        )

    @property
    def no(self):
        return Boolean(not self.value)

__all__ = ('Boolean',)
