import importlib
import abc
from typing import GenericMeta, Dict
from functools import partial

from tryp.util.string import snake_case
from tryp.lazy import lazy
from tryp.tc.show import Show


class TypeClass(object, metaclass=abc.ABCMeta):
    pass


class TypeClasses(object):

    @property
    def instances(self):
        pass


class ImplicitInstancesNotFound(Exception):

    def __init__(self, mod, cls, name):
        msg = 'invalid implicit class path {}.{} for {}'.format(mod, cls, name)
        super().__init__(msg)


class ImplicitsMeta(GenericMeta):

    def _infer_implicits(name):
        snake = snake_case(name)
        return 'tryp.{}'.format(snake), '{}Instances'.format(name)

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
                    Instances = getattr(mod, imp_cls)
                    inst.implicits = Instances()
                    return inst
                else:
                    raise err


def tc_prop(f):
    f._tc_prop = True
    return f


class Implicits(object, metaclass=ImplicitsMeta):

    def __getattr__(self, name):
        for inst in self.implicits.instances.values:
            if hasattr(inst, name):
                f = getattr(inst, name)
                if hasattr(f, '_tc_prop'):
                    return f(self)
                else:
                    return partial(f, self)
        err = '\'{}\' has no attribute \'{}\''.format(self, name)
        raise AttributeError(err)


class ImplicitInstances(object, metaclass=abc.ABCMeta):

    @lazy
    def instances(self):
        return (TC.instances ** self._instances **
                self._override_instances)

    @abc.abstractproperty
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
        return Map({Show: Show()})


TC = GlobalTypeClasses()

__all__ = ('TypeClasses', 'TC')
