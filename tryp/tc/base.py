import importlib
import abc
from typing import GenericMeta, Dict
from functools import partial

from fn import _, F

from tryp.util.string import snake_case
from tryp.lazy import lazy
from tryp.tc.show import Show


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
)


class ImplicitsMeta(GenericMeta):

    def _infer_implicits(name):
        snake = snake_case(name)
        return 'tryp.{}'.format(snake), '{}Instances'.format(name)

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
            err = ImplicitInstancesNotFound(imp_mod, imp_cls, name)
            if imp_mod is None or imp_cls is None:
                imp_mod, imp_cls = ImplicitsMeta._infer_implicits(name)
            try:
                mod = importlib.import_module(imp_mod)
            except ImportError:
                raise err
            else:
                if hasattr(mod, imp_cls):
                    instances = getattr(mod, imp_cls)()
                    inst.implicits = instances
                    Instances.add(name, instances)
                    ImplicitsMeta._attach_operators(inst)
                    return inst
                else:
                    raise err


def tc_prop(f):
    f._tc_prop = True
    return f


class Implicits(object, metaclass=ImplicitsMeta):

    def _lookup_implicit_attr(self, name):
        for inst in self.implicits.instances.values:
            if hasattr(inst, name):
                f = getattr(inst, name)
                if hasattr(f, '_tc_prop'):
                    return f(self)
                else:
                    return partial(f, self)

    def __getattr__(self, name):
        imp = self._lookup_implicit_attr(name)
        if imp is None:
            err = '\'{}\' has no attribute \'{}\''.format(self, name)
            raise AttributeError(err)
        else:
            return imp

    def _operator(self, name, other):
        op = self._lookup_implicit_attr(name)
        if op is None:
            err = '\'{}\' has no implicit operator \'{}\''.format(self, name)
            raise TypeError(err)
        else:
            return op(other)


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
        from tryp.map import Map
        return Map()


class GlobalTypeClasses(TypeClasses):

    @property
    def instances(self):
        from tryp.map import Map
        from tryp.tc.tap import Tap
        return Map({Show: Show(), Tap: Tap()})


TC = GlobalTypeClasses()


class ImplicitNotFound(Exception):

    def __init__(self, tc, a):
        msg = 'no type class found for {}[{}]'.format(tc, a)
        super().__init__(msg)


class AllInstances(object):

    def __init__(self):
        self._instances = dict()

    def add(self, name, inst: ImplicitInstances):
        self._instances[name] = inst

    def lookup(self, TC, G):
        ''' Find an instance of the type class `TC` for type `G`.
        Iterates `G`'s parent classes, looking up instances for each,
        checking whether the instance is a subclass of the target type
        class @`C`.
        '''
        from tryp.lazy_list import LazyList
        match = F(self._lookup_type, TC)
        result = LazyList(map(match, G.__mro__))\
            .find(_.is_just)\
            .flatten\
            .get_or_raise(ImplicitNotFound(TC, G))
        return result[1]

    def _lookup_type(self, TC, G):
        from tryp.maybe import Empty
        if G.__name__ in self._instances:
            match = lambda I: isinstance(I, TC)
            return self._instances[G.__name__].instances.find(match)
        else:
            return Empty()

Instances = AllInstances()  # type: AllInstances

__all__ = ('TypeClasses', 'TC', 'tc_prop', 'TypeClass')
