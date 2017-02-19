import importlib
import abc
from typing import Dict, Tuple, Any, Callable, Union, Optional, GenericMeta
from typing import List  # NOQA
from functools import partial, wraps

import amino  # NOQA
from amino.util.string import snake_case
from amino.lazy import lazy
from amino.tc.show import Show

from amino.logging import amino_root_logger


class TypeClassMeta(GenericMeta):

    def __new__(cls: type, name: str, bases: tuple, namespace: dict,
                tpe: type=None, pred: Callable=None, **kw: dict) -> type:
        inst = super().__new__(cls, name, bases, namespace,  # type: ignore
                               **kw)
        if name != 'TypeClass':
            if tpe is not None:
                Instances.add_auto(tpe, inst())
            elif pred is not None:
                Instances.add_pred(pred, inst())
        return inst

    def fatal(self, tpe: type) -> 'TypeClass':
        return Instances.lookup(self, tpe)

    def fatal_for(self, a: Any) -> 'amino.maybe.Maybe[TypeClass]':
        return self.fatal(type(a))

    def __getitem__(self, tpe: type) -> 'TypeClass':
        return self.fatal(tpe)

    def m(self, tpe: type) -> 'amino.maybe.Maybe[TypeClass]':
        return Instances.lookup_m(self, tpe)

    def m_for(self, a: Any) -> 'amino.maybe.Maybe[TypeClass]':
        return self.m(type(a))

    def exists_instance(self, tpe: type) -> bool:
        try:
            self[tpe]
        except ImplicitNotFound:
            return False
        else:
            return True

    exists = exists_instance


class TypeClass(metaclass=TypeClassMeta):
    pass


class TypeClasses:

    @property
    def instances(self) -> Dict[type, TypeClass]:
        pass


class ImplicitInstancesNotFound(Exception):

    def __init__(self, mod: str, cls: str, name: str) -> None:
        msg = 'invalid implicit class path {}.{} for {}'.format(mod, cls, name)
        super().__init__(msg)


operators = (
    '__floordiv__',
    '__truediv__',
    '__mod__',
    '__or__',
    '__and__',
)


class ImplicitInstancesMeta(abc.ABCMeta):

    def __new__(cls: type, name: str, bases: tuple, namespace: dict,
                tpe: type=None, **kw: dict) -> type:
        inst = super().__new__(cls, name, bases, namespace,  # type: ignore
                               **kw)
        if name != 'ImplicitInstances' and tpe is not None:
            Instances.add_instances(tpe, inst())
        return inst


class ImplicitInstances(metaclass=ImplicitInstancesMeta):

    @lazy
    def instances(self) -> Dict[type, TypeClass]:
        return (
            TC.instances ** self._instances **  # type: ignore
            self._override_instances
        )

    @abc.abstractproperty
    def _instances(self) -> Dict[type, TypeClass]:
        ...

    @property
    def _override_instances(self) -> Dict[type, TypeClass]:
        from amino.map import Map
        return Map()


def lookup_implicit_instances(name: str, m: str, c: str) -> ImplicitInstances:
    err = ImplicitInstancesNotFound(m, c, name)
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


class InstancesMetadata:

    def __init__(self, name: str, mod: str, cls: str) -> None:
        self.name = name
        self.mod = mod
        self.cls = cls
        self._instances = None  # type: Optional[ImplicitInstances]

    def __str__(self) -> str:
        return '{}({}, {}, {})'.format(self.__class__.__name__, self.name,
                                       self.mod, self.cls)

    @property
    def instances(self) -> Dict[str, TypeClass]:
        if self._instances is None:
            self._instances = lookup_implicit_instances(self.name, self.mod,
                                                        self.cls)
        return self._instances.instances


def _infer_implicits(name: str) -> Tuple[str, str]:
    snake = snake_case(name)
    return 'amino.instances.{}'.format(snake), '{}Instances'.format(name)


class ImplicitsMeta(GenericMeta):

    @staticmethod
    def _mk_operator(name: str) -> Callable:
        def dispatch(self: Any, other: Any) -> Any:
            return self._operator(name, other)
        return dispatch

    def _attach_operators(inst) -> None:
        for op in operators:
            setattr(inst, op, ImplicitsMeta._mk_operator(op))

    def __new__(cls: type, name: str, bases: tuple, namespace: dict,
                imp_mod: str=None, imp_cls: str=None, implicits: bool=False,
                **kw: dict) -> type:
        inst = super().__new__(cls, name, bases, namespace,  # type: ignore
                               **kw)
        if not implicits:
            inst._instances_meta = None
            return inst
        else:
            if imp_mod is None or imp_cls is None:
                imp_mod, imp_cls = _infer_implicits(name)
            inst.name = name
            ImplicitsMeta._attach_operators(inst)
            meta = InstancesMetadata(name, imp_mod, imp_cls)
            inst.imp_mod = imp_mod
            inst.imp_cls = imp_cls
            inst.instances_meta = meta
            Instances.add(meta)
            return inst

    __copy__ = None


def tc_prop(f: Callable) -> Callable:
    f._tc_prop = True  # type: ignore
    return f


class Implicits(metaclass=ImplicitsMeta):
    permanent = True

    def _lookup_implicit_attr(self, name: str) -> Optional[Callable]:
        meta = type(self).instances_meta  # type: ignore
        if meta is not None:
            return next((getattr(inst, name)
                        for inst in meta.instances.v
                        if hasattr(inst, name)), None)

    def _bound_implicit_attr(self, name: str
                             ) -> Union[None, Callable, partial]:
        f = self._lookup_implicit_attr(name)
        if f is not None:
            if hasattr(f, '_tc_prop'):
                return f(self)
            else:
                return partial(f, self)
        return None

    def _set_implicit_attr(self, name: str) -> Any:
        f = self._lookup_implicit_attr(name)
        if f is not None:
            @wraps(f)
            def wrap(self: Any, *a: Any, **kw: Any) -> Any:
                return f(self, *a, **kw)  # type: ignore
            g = property(wrap) if hasattr(f, '_tc_prop') else wrap
            setattr(type(self), name, g)
            return getattr(self, name)

    def __getattr__(self, name: str) -> Callable:
        imp = (self._set_implicit_attr(name) if Implicits.permanent else
               self._bound_implicit_attr(name))
        if imp is None:
            err = '\'{}\' has no attribute \'{}\''.format(self, name)
            raise AttributeError(err)
        else:
            return imp

    def _operator(self, name: str, other: Any) -> Any:
        op = (self._set_implicit_attr(name) if Implicits.permanent else
              self._bound_implicit_attr(name))
        if op is None:
            err = '\'{}\' has no implicit operator \'{}\''.format(self, name)
            raise TypeError(err)
        else:
            return op(other)

    @property
    def dbg(self) -> Any:
        amino_root_logger.verbose(self)
        return self

    @property
    def dbgr(self) -> Any:
        v = self.log.verbose  # type: ignore
        v(repr(self))
        return self


class GlobalTypeClasses(TypeClasses):

    @property
    def instances(self) -> Dict[type, TypeClass]:
        from amino.map import Map
        from amino.tc.tap import Tap
        return Map({Show: Show(), Tap: Tap()})


TC = GlobalTypeClasses()


class ImplicitNotFound(Exception):

    def __init__(self, tc: type, a: type) -> None:
        msg = 'no type class found for {}[{}]'.format(tc, a)
        super().__init__(msg)


class AutoImplicitInstances(ImplicitInstances):

    def __init__(self, tpe: type, instance: TypeClass) -> None:
        self.tpe = tpe
        self.instance = instance

    @lazy
    def _instances(self) -> Dict[type, TypeClass]:
        from amino import Map
        return Map({self.tpe: self.instance})


class NoTypeClass(Exception):

    def __init__(self, inst: Any) -> None:
        super().__init__('invalid type class: {}'.format(inst))


class PredTypeClass:

    def __init__(self, pred: Callable[[type], bool], tc: TypeClass) -> None:
        self.pred = pred
        self.tc = tc


class AllInstances:

    def __init__(self) -> None:
        self.instances = dict()  # type: Dict[str, InstancesMetadata]
        self.auto_instances = dict()  # type: Dict[type, ImplicitInstances]
        self.pred_instances = (
            dict())  # type: Dict[type, amino.list.List[PredTypeClass]]

    def add(self, data: InstancesMetadata) -> None:
        self.instances[data.name] = data

    def add_instances(self, tpe: type, instances: ImplicitInstances) -> None:
        if tpe in self.auto_instances:
            self.auto_instances[tpe].instances.update(instances._instances)
        else:
            self.auto_instances[tpe] = instances

    def _tc_type(self, inst: TypeClass) -> type:
        mro = inst.__class__.__mro__
        if len(mro) < 2 or TypeClass not in mro:
            raise NoTypeClass(inst)
        return mro[1]

    def add_auto(self, tpe: type, inst: TypeClass) -> None:
        tc_type = self._tc_type(inst)
        self.add_instances(tpe, AutoImplicitInstances(tc_type, inst))

    def add_pred(self, pred: Callable[[type], bool], inst: TypeClass) -> None:
        import amino.list
        tc_type = self._tc_type(inst)
        data = PredTypeClass(pred, inst)
        if tc_type in self.pred_instances:
            self.pred_instances[tc_type].append(data)
        else:
            self.pred_instances[tc_type] = amino.list.List(data)

    def lookup(self, TC: type, G: type) -> TypeClass:
        return self.lookup_m(TC, G).get_or_raise(ImplicitNotFound(TC, G))

    def lookup_m(self, TC: type, G: type) -> 'amino.maybe.Maybe[TypeClass]':
        ''' Find an instance of the type class `TC` for type `G`.
        Iterates `G`'s parent classes, looking up instances for each,
        checking whether the instance is a subclass of the target type
        class `TC`.
        '''
        from amino.lazy_list import LazyList
        from amino.anon import _
        match = lambda a: self._lookup_type(TC, a)
        def attach_type(tc: TypeClass) -> None:
            tc.tpe = G
        return (
            LazyList(map(match, G.__mro__))
            .find(_.is_just)
            .join
            .foreach(attach_type)
        )

    def _lookup_type(self, TC: type, G: type
                     ) -> 'amino.maybe.Maybe[TypeClass]':
        return (
            self._lookup_auto(TC, G)
            .o(lambda: self._lookup_regular(TC, G))
            .o(lambda: self._lookup_pred(TC, G))
        )

    def _lookup_auto(self, TC: type, G: type
                     ) -> 'amino.maybe.Maybe[TypeClass]':
        from amino.maybe import Empty
        if G in self.auto_instances:
            return (
                self.auto_instances[G].instances
                .find(lambda I: isinstance(I, TC))
                .map(lambda a: a[1])
            )
        else:
            return Empty()

    def _lookup_regular(self, TC: type, G: type
                        ) -> 'amino.maybe.Maybe[TypeClass]':
        from amino.maybe import Empty
        if G.__name__ in self.instances:
            return (
                self.instances[G.__name__].instances
                .find(lambda I: isinstance(I, TC))
                .map(lambda a: a[1])
            )
        else:
            return Empty()

    def _lookup_pred(self, TC: type, G: type
                     ) -> 'amino.maybe.Maybe[TypeClass]':
        from amino.maybe import Empty
        if TC in self.pred_instances:
            return (
                self.pred_instances[TC]
                .find(lambda a: a.pred(G))
                .map(lambda a: a.tc)
            )
        return Empty()

Instances = AllInstances()  # type: AllInstances

__all__ = ('TypeClasses', 'TC', 'tc_prop', 'TypeClass')
