import importlib
import abc
from typing import Dict, Callable
from typing import GenericMeta  # type: ignore
from functools import partial, wraps

from amino.util.string import snake_case
from amino.lazy import lazy
from amino.tc.show import Show

from amino.logging import Logging


class TypeClassMeta(GenericMeta):

    def __getitem__(self, tpe: type):
        return Instances.lookup(self, tpe)

    def exists(self, tpe: type):
        try:
            self[tpe]
        except ImplicitNotFound:
            return False
        else:
            return True


class TypeClass(object, metaclass=TypeClassMeta):
    pass


class TypeClasses(object):

    @property
    def instances(self):
        pass


class ImplicitInstancesNotFound(Exception):

    def __init__(self, mod, cls, name):
        msg = 'invalid implicit class path {}.{} for {}'.format(mod, cls, name)
        super().__init__(msg)


operators = (
    '__floordiv__',
    '__truediv__',
    '__mod__',
    '__or__',
    '__and__',
)


class ImplicitsMeta(GenericMeta):

    def _infer_implicits(name):
        snake = snake_case(name)
        return 'amino.instances.{}'.format(snake), '{}Instances'.format(name)

    def _mk_operator(name):
        def dispatch(self, other):
            return self._operator(name, other)
        return dispatch

    def _attach_operators(inst):
        for op in operators:
            setattr(inst, op, ImplicitsMeta._mk_operator(op))

    def __new__(cls, name, bases, namespace, imp_mod=None, imp_cls=None,
                implicits=False, **kw):
        inst = super().__new__(cls, name, bases, namespace, **kw)
        if not implicits:
            return inst
        else:
            if imp_mod is None or imp_cls is None:
                imp_mod, imp_cls = ImplicitsMeta._infer_implicits(name)
            inst.imp_mod = imp_mod
            inst.imp_cls = imp_cls
            inst.name = name
            inst._implicits_instance = None
            ImplicitsMeta._attach_operators(inst)
            Instances.add(name, inst)
            return inst

    @property
    def _implicits(self):
        m = self.imp_mod
        c = self.imp_cls
        err = ImplicitInstancesNotFound(m, c, self.name)
        try:
            mod = importlib.import_module(m)
        except ImportError:
            raise err
        else:
            if hasattr(mod, c):
                instances = getattr(mod, c)()
                return instances
            else:
                raise err

    @property
    def implicits(self):
        if self._implicits_instance is None:
            self._implicits_instance = self._implicits.instances
        return self._implicits_instance


def tc_prop(f):
    f._tc_prop = True
    return f


class Implicits(Logging, metaclass=ImplicitsMeta):
    permanent = True

    def _lookup_implicit_attr(self, name):
        return next((getattr(inst, name)
                     for inst in type(self).implicits.v
                     if hasattr(inst, name)), None)

    def _bound_implicit_attr(self, name):
        f = self._lookup_implicit_attr(name)
        if f is not None:
            if hasattr(f, '_tc_prop'):
                return f(self)
            else:
                return partial(f, self)

    def _set_implicit_attr(self, name):
        f = self._lookup_implicit_attr(name)
        if f is not None:
            @wraps(f)
            def wrap(self, *a, **kw):
                return f(self, *a, **kw)
            g = property(wrap) if hasattr(f, '_tc_prop') else wrap
            setattr(type(self), name, g)
            return getattr(self, name)

    def __getattr__(self, name):
        imp = (self._set_implicit_attr(name) if Implicits.permanent else
               self._bound_implicit_attr(name))
        if imp is None:
            err = '\'{}\' has no attribute \'{}\''.format(self, name)
            raise AttributeError(err)
        else:
            return imp

    def _operator(self, name, other):
        op = (self._set_implicit_attr(name) if Implicits.permanent else
              self._bound_implicit_attr(name))
        if op is None:
            err = '\'{}\' has no implicit operator \'{}\''.format(self, name)
            raise TypeError(err)
        else:
            return op(other)

    @property
    def dbg(self):
        v = self.log.verbose
        v(self)
        return self

    @property
    def dbgr(self):
        v = self.log.verbose
        v(repr(self))
        return self


class ImplicitInstances(object, metaclass=abc.ABCMeta):

    @lazy
    def instances(self):
        return (TC.instances ** self._instances **
                self._override_instances)

    @abc.abstractproperty  # type: ignore
    def _instances(self) -> Dict[type, TypeClass]:
        ...

    @property
    def _override_instances(self) -> Dict[type, TypeClass]:
        from amino.map import Map
        return Map()


class GlobalTypeClasses(TypeClasses):

    @property
    def instances(self):
        from amino.map import Map
        from amino.tc.tap import Tap
        return Map({Show: Show(), Tap: Tap()})


TC = GlobalTypeClasses()


class ImplicitNotFound(Exception):

    def __init__(self, tc, a):
        msg = 'no type class found for {}[{}]'.format(tc, a)
        super().__init__(msg)


class AllInstances(object):

    def __init__(self):
        self._instances = dict()

    def add(self, name, inst: Callable[[], ImplicitInstances]):
        self._instances[name] = inst

    def lookup(self, TC, G):
        ''' Find an instance of the type class `TC` for type `G`.
        Iterates `G`'s parent classes, looking up instances for each,
        checking whether the instance is a subclass of the target type
        class @`C`.
        '''
        from amino.lazy_list import LazyList
        from amino.anon import _, L
        match = L(self._lookup_type)(TC, _)
        result = LazyList(map(match, G.__mro__))\
            .find(_.is_just)\
            .join\
            .get_or_raise(ImplicitNotFound(TC, G))
        return result[1]

    def _lookup_type(self, TC, G):
        from amino.maybe import Empty
        if G.__name__ in self._instances:
            match = lambda I: isinstance(I, TC)
            return self._instances[G.__name__].implicits.find(match)
        else:
            return Empty()

Instances = AllInstances()  # type: AllInstances

__all__ = ('TypeClasses', 'TC', 'tc_prop', 'TypeClass')
