class AnonFunc(object):

    def __init__(self, name, a, kw):
        self.name = name
        self.a = a
        self.kw = kw

    def __call__(self, obj):
        if not hasattr(obj, self.name):
            raise AttributeError(
                '{!r} has no method \'{}\''.format(obj, self.name))
        return getattr(obj, self.name)(*self.a, **self.kw)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.name)


class MethodRef(object):

    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, *a, **kw):
        return AnonFunc(self.name, a, kw)


class MethodLambda(object):

    def __getattr__(self, name):
        return MethodRef(name)

__ = MethodLambda()

__all__ = ('__', )
