from functools import wraps, partial
from inspect import getfullargspec

import fn


class F(fn.F):

    def __truediv__(self, f):
        return self >> (lambda a: a / f)

    def __floordiv__(self, f):
        return self >> (lambda a: a // f)

    @property
    def name(self):
        f = self.f.func if self._is_partial else self.f
        return f.__name__

    @property
    def _is_partial(self):
        return isinstance(self.f, partial)

    def __repr__(self):
        from amino.anon import format_funcall
        rep = (format_funcall(self.name, self.f.args, self.f.keywords)
               if self._is_partial
               else '{}()'.format(self.name))
        return 'F({})'.format(rep)


def curried(func):
    @wraps(func)
    def _curried(*args, **kwargs):
        f = func
        count = 0
        while isinstance(f, partial):
            if f.args:
                count += len(f.args)
            f = f.func
        spec = getfullargspec(f)
        if count == len(spec.args) - len(args):
            return func(*args, **kwargs)
        else:
            return curried(partial(func, *args, **kwargs))
    return _curried


class Identity:

    def __call__(self, a):
        return a

    def __repr__(self):
        return 'a => a'

I = Identity()

__all__ = ('curried', 'F', 'I')
