from operator import methodcaller


class FuncRef(object):

    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, *a, **kw):
        return methodcaller(self.name, *a, **kw)


class Lambda(object):

    def __getattr__(self, name):
        return FuncRef(name)

__ = Lambda()

__all__ = ('__')
