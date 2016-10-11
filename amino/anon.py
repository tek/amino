from types import FunctionType, MethodType
import operator

from amino import List, Boolean


class AnonError(Exception):
    pass


def lambda_str(f):
    if isinstance(f, MethodType):
        return '{}.{}'.format(f.__self__.__class__.__name__, f.__name__)
    elif isinstance(f, FunctionType):
        return f.__name__
    elif isinstance(f, str):
        return f
    else:
        return str(f)


def format_funcall(fun, args, kwargs):
    from amino import Map
    kw = Map(kwargs).map2('{}={!r}'.format)
    a = list(map(repr, args)) + list(kw)
    args_fmt = ', '.join(a)
    return '{}({})'.format(lambda_str(fun), args_fmt)


class AnonCallable:

    def __call_as_pre__(self, obj, a):
        return self(obj), a

    def __call__(self, obj):
        return obj


class AnonGetter(AnonCallable):

    def __init__(self, pre, name: str) -> None:
        self.__pre = pre
        self.__name = name

    def __repr__(self):
        return '{}.{}'.format(self.__pre, self.__name)

    def __call_as_pre__(self, obj, a):
        return self.__call(obj, a)

    def __call_pre(self, obj, a):
        pre, rest = self.__pre.__call_as_pre__(obj, a)
        if not hasattr(pre, self.__name):
            raise AttributeError('{!r} has no method \'{}\' -> {!r}'.format(
                pre, self.__name, self))
        return pre, rest

    def __call(self, obj, a):
        pre, rest = self.__call_pre(obj, a)
        return self.__dispatch__(getattr(pre, self.__name), rest)

    def __call__(self, obj, *a):
        result, rest = self.__call(obj, List.wrap(a))
        if not rest.empty:
            msg = 'extraneous arguments to {}: {}'
            raise AnonError(msg.format(self, rest.mk_string(',')))
        return result

    def __dispatch__(self, obj, a):
        return obj, a


class HasArgs:

    def __substitute__(self, params, args):
        def go(z, arg):
            def transform(value):
                return arg(value) if isinstance(arg, AnonCallable) else value
            def try_sub(new, rest):
                is_lambda = Boolean(arg is _ or isinstance(arg, AnonCallable))
                return is_lambda.m(lambda: (transform(new), rest))
            r, a = z
            new, rest = a.detach_head.flat_map2(try_sub) | (arg, a)
            return r.cat(new), rest
        subbed, rest = params.fold_left((List(), args))(go)
        # allow callables to remain in args, but not placeholders
        if rest.empty and subbed.exists(lambda a: a is _):
            raise AnonError('too few arguments for {}: {}'.format(self, args))
        return subbed, rest


class AnonFunc(AnonGetter, HasArgs):

    def __init__(self, pre: 'AnonFunc', name: str, a, kw) -> None:
        super().__init__(pre, name)
        self.__args = List.wrap(a)
        self.__kw = kw

    def __dispatch__(self, obj, a):
        sub_a, rest = self.__substitute__(self.__args, List.wrap(a))
        return obj(*sub_a, **self.__kw), rest

    def __getattr__(self, name):
        return MethodRef(self, name)

    def __repr__(self):
        return '{!r}.{}'.format(
            self._AnonGetter__pre,
            format_funcall(self._AnonGetter__name, self.__args, self.__kw)
        )

    def __getitem__(self, key):
        return AnonFunc(self, '__getitem__', [key], {})


class MethodRef:

    def __init__(self, pre: AnonFunc, name: str) -> None:
        self.__pre = pre
        self.__name = name

    def __call__(self, *a, **kw):
        return AnonFunc(self.__pre, self.__name, a, kw)

    def __getattr__(self, name):
        pre = AnonGetter(self.__pre, self.__name)
        return MethodRef(pre, name)

    def __repr__(self):
        return '__.{}'.format(self.__name)


class IdAnonFunc(AnonCallable):

    def __repr__(self):
        return '__'


class AnonCall(AnonFunc):

    def __init__(self, pre, a, kw) -> None:
        super().__init__(pre, '__call__', a, kw)

    def __call__(self, obj, *a, **kw):
        return self._AnonGetter__pre(obj)(
            *self._AnonFunc__args, **self._AnonFunc__kw)


class MethodLambda:

    def __getattr__(self, name):
        return MethodRef(IdAnonFunc(), name)

    def __call__(self, *a, **kw):
        return AnonCall(IdAnonFunc(), a, kw)

    def __getitem__(self, key):
        return AnonFunc(IdAnonFunc(), '__getitem__', [key], {})

__ = MethodLambda()


class ComplexLambda(AnonCallable, HasArgs):

    def __init__(self, func, *a, **kw) -> None:
        assert callable(func), 'ComplexLambda: {} is not callable'.format(func)
        self.__func = func
        self.__args = List.wrap(a)
        self.__kwargs = kw

    def __call__(self, *a, **kw):
        sub_a, rest = self.__substitute__(self.__args, List.wrap(a))
        return self.__func(*sub_a, **kw)

    def __getattr__(self, name):
        return MethodRef(self, name)

    @property
    def __name(self):
        return getattr(self.__func, '__name__', str(self.__func))

    def __repr__(self):
        return format_funcall(self.__name, self.__args, self.__kwargs)


class L:

    def __init__(self, func) -> None:
        self.__func = func

    def __call__(self, *a, **kw):
        return ComplexLambda(self.__func, *a, **kw)


def lambda_op(op, s):
    def oper(self, a):
        return OperatorLambda(self.__anon_func__, op, a, s, False)
    return oper


def lambda_rop(op, s):
    def oper(self, a):
        return OperatorLambda(self.__anon_func__, op, a, s, True)
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
        return AttrLambda(self.__anon_func__, name)

    @property
    def __anon_func__(self):
        return IdAttrLambda()

    def __repr__(self):
        return '_'


class AttrLambda(Opers, AnonGetter, AnonCallable):

    def __init__(self, pre: 'AttrLambda', name: str) -> None:
        super().__init__(pre, name)

    def __getattr__(self, name):
        return AttrLambda(self, name)

    @property
    def __anon_func__(self):
        return self

    def __repr__(self):
        return '{}.{}'.format(self._AnonGetter__pre, self._AnonGetter__name)


class OperatorLambda(AttrLambda):

    def __init__(self, pre: 'AttrLambda', op, strict, name, right) -> None:
        super().__init__(pre, name)
        self.__op = op
        self.__strict = strict
        self.__right = right

    def __call__(self, obj):
        pre = self._AnonGetter__pre(obj)
        a, b = (self.__strict, pre) if self.__right else (pre, self.__strict)
        return self.__op(a, b)

    def __repr__(self):
        a, b = (
            (self.__strict, self._AnonGetter__pre)
            if self.__right
            else (self._AnonGetter__pre, self.__strict)
        )
        return '({!r} {} {!r})'.format(a, self._AnonGetter__name, b)

_ = RootAttrLambda()

__all__ = ('__', 'L', '_')
