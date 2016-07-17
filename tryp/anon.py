from fn import _

from tryp import List

class AnonGetter:

    def __init__(self, pre: 'AnonFunc', name: str) -> None:
        self.pre = pre
        self.name = name

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.name)

    def __call__(self, obj):
        pre = self.pre(obj)
        if not hasattr(pre, self.name):
            raise AttributeError(
                '{!r} has no method \'{}\' => {}'.format(obj, self.name, self))
        return self._dispatch(getattr(pre, self.name))

    def _dispatch(self, obj):
        return obj


class AnonFunc(AnonGetter):

    def __init__(self, pre: 'AnonFunc', name: str, a, kw) -> None:
        super().__init__(pre, name)
        self.a = a
        self.kw = kw

    def _dispatch(self, obj):
        return obj(*self.a, **self.kw)

    def __getattr__(self, name):
        return MethodRef(self, name)

    def __repr__(self):
        from tryp import Map
        kw = Map(self.kw).map2('{}={!r}'.format)
        a = list(map(repr, self.a)) + list(kw)
        args = ', '.join(a)
        return '{!r}.{}({})'.format(self.pre, self.name, args)


class MethodRef:

    def __init__(self, pre: AnonFunc, name: str) -> None:
        self.pre = pre
        self.name = name

    def __call__(self, *a, **kw):
        return AnonFunc(self.pre, self.name, a, kw)

    def __getattr__(self, name):
        pre = AnonGetter(self.pre, self.name)
        return MethodRef(pre, name)

    def __repr__(self):
        return '__.{}'.format(self.name)


class IdAnonFunc:

    def __call__(self, obj):
        return obj

    def __repr__(self):
        return '__'


class MethodLambda:

    def __getattr__(self, name):
        return MethodRef(IdAnonFunc(), name)

__ = MethodLambda()


class ComplexLambda:

    def __init__(self, func, *a, **kw) -> None:
        self.func = func
        self.args = List.wrap(a)
        self.kwargs = kw

    def __call__(self, *a, **kw):
        sub_a = self._substitute(List.wrap(a))
        return self.func(*sub_a, **kw)

    def _substitute(self, args):
        def errmsg():
            return 'too few arguments for lambda "{}": {}'.format(self, args)
        def go(z, arg):
            r, a = z
            new, rest = (a.detach_head.get_or_raise(errmsg()) if arg is _ else
                         (arg, a))
            return r.cat(new), rest
        return self.args.fold_left((List(), args))(go)[0]


class L:

    def __init__(self, func) -> None:
        self.func = func

    def __call__(self, *a, **kw):
        return ComplexLambda(self.func, *a, **kw)


__all__ = ('__', 'L')
