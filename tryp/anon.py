import operator

from tryp import List


def format_funcall(fun, args, kwargs):
    from tryp import Map
    kw = Map(kwargs).map2('{}={!r}'.format)
    a = list(map(repr, args)) + list(kw)
    args_fmt = ', '.join(a)
    return '{}({})'.format(fun, args_fmt)


class AnonCallable:

    def __call__(self, obj):
        return obj


class AnonGetter(AnonCallable):

    def __init__(self, pre, name: str) -> None:
        self.pre = pre
        self.name = name

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.name)

    def __call__(self, obj):
        pre = self.pre(obj)
        if not hasattr(pre, self.name):
            raise AttributeError(
                '{!r} has no method \'{}\' -> {}'.format(obj, self.name, self))
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
        return '{!r}.{}'.format(self.pre,
                                format_funcall(self.name, self.a, self.kw))


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
        assert callable(func), 'ComplexLambda: {} is not callable'.format(func)
        self.func = func
        self.args = List.wrap(a)
        self.kwargs = kw

    def __call__(self, *a, **kw):
        sub_a = self._substitute(List.wrap(a))
        return self.func(*sub_a, **kw)

    def _substitute(self, args):
        def errmsg():
            return 'too few arguments for lambda "{}": {}'.format(self, args)
        def is_lambda(arg):
            return arg is _ or isinstance(arg, AnonCallable)
        def go(z, arg):
            def transform(value):
                return arg(value) if isinstance(arg, AnonCallable) else value
            r, a = z
            new, rest = (a.detach_head.get_or_fail(errmsg()) if is_lambda(arg)
                         else (arg, a))
            return r.cat(transform(new)), rest
        return self.args.fold_left((List(), args))(go)[0]

    def __getattr__(self, name):
        return MethodRef(self, name)

    def __repr__(self):
        return format_funcall(self.func.__name__, self.args, self.kwargs)


class L:

    def __init__(self, func) -> None:
        self.func = func

    def __call__(self, *a, **kw):
        return ComplexLambda(self.func, *a, **kw)


def lambda_op(op, s):
    def oper(self, a):
        return OperatorLambda(self._anon_func, op, a, s, False)
    return oper


def lambda_rop(op, s):
    def oper(self, a):
        return OperatorLambda(self._anon_func, op, a, s, True)
    return oper


class Opers:

    __getitem__ = lambda_op(operator.getitem, "getitem")
    __add__ = lambda_op(operator.add, "+")
    __mul__ = lambda_op(operator.mul, "*")
    __sub__ = lambda_op(operator.sub, "-")
    __mod__ = lambda_op(operator.mod, "%%")
    __pow__ = lambda_op(operator.pow, "**")
    __and__ = lambda_op(operator.and_, "&")
    __or__ = lambda_op(operator.or_, "|")
    __xor__ = lambda_op(operator.xor, "^")
    __div__ = lambda_op(operator.truediv, "/")
    __divmod__ = lambda_op(divmod, "/")
    __floordiv__ = lambda_op(operator.floordiv, "/")
    __truediv__ = lambda_op(operator.truediv, "/")
    __lshift__ = lambda_op(operator.lshift, "<<")
    __rshift__ = lambda_op(operator.rshift, ">>")
    __lt__ = lambda_op(operator.lt, "<")
    __le__ = lambda_op(operator.le, "<=")
    __gt__ = lambda_op(operator.gt, ">")
    __ge__ = lambda_op(operator.ge, ">=")
    __eq__ = lambda_op(operator.eq, "==")
    __ne__ = lambda_op(operator.ne, "!=")
    # __neg__ = unary_lambda_op(operator.neg, "-self")
    # __pos__ = unary_lambda_op(operator.pos, "+self")
    # __invert__ = unary_lambda_op(operator.invert, "~self")
    __radd__ = lambda_rop(operator.add, "+")
    __rmul__ = lambda_rop(operator.mul, "*")
    __rsub__ = lambda_rop(operator.sub, "-")
    __rmod__ = lambda_rop(operator.mod, "%%")
    __rpow__ = lambda_rop(operator.pow, "**")
    __rdiv__ = lambda_rop(operator.truediv, "/")
    __rdivmod__ = lambda_rop(divmod, "/")
    __rtruediv__ = lambda_rop(operator.truediv, "/")
    __rfloordiv__ = lambda_rop(operator.floordiv, "/")
    __rlshift__ = lambda_rop(operator.lshift, "<<")
    __rrshift__ = lambda_rop(operator.rshift, ">>")
    __rand__ = lambda_rop(operator.and_, "&")
    __ror__ = lambda_rop(operator.or_, "|")
    __rxor__ = lambda_rop(operator.xor, "^")


class IdAttrLambda(IdAnonFunc):

    def __repr__(self):
        return '_'


class RootAttrLambda(Opers):

    def __getattr__(self, name):
        return AttrLambda(self._anon_func, name)

    @property
    def _anon_func(self):
        return IdAttrLambda()

    def __repr__(self):
        return '_'


class AttrLambda(Opers, AnonGetter, AnonCallable):

    def __init__(self, pre: 'AttrLambda', name: str) -> None:
        super().__init__(pre, name)

    def __getattr__(self, name):
        return AttrLambda(self, name)

    @property
    def _anon_func(self):
        return self

    def __repr__(self):
        return '{}.{}'.format(self.pre, self.name)


class OperatorLambda(AttrLambda):

    def __init__(self, pre: 'AttrLambda', op, strict, name, right) -> None:
        super().__init__(pre, name)
        self.op = op
        self.strict = strict
        self.right = right

    def __call__(self, obj):
        pre = self.pre(obj)
        a, b = (self.strict, pre) if self.right else (pre, self.strict)
        return self.op(a, b)

    def __repr__(self):
        a, b = (
            (self.strict, self.pre)
            if self.right
            else (self.pre, self.strict)
        )
        return '({!r} {} {!r})'.format(a, self.name, b)

_ = RootAttrLambda()

__all__ = ('__', 'L', '_')
