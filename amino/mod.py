from typing import Any, Callable, TypeVar, Type
from types import ModuleType

from amino.do import do, Do
from amino import Maybe, Lists, L, _, Either, List


@do(Either[str, List[Any]])
def objects_from_module(mod: ModuleType, pred: Callable[[Any], bool]) -> Do:
    all = yield Maybe.getattr(mod, '__all__').to_either(f'module `{mod.__name__}` does not define `__all__`')
    return (
        Lists.wrap(all)
        .flat_map(L(Maybe.getattr)(mod, _))
        .filter(pred)
    )


@do(Either[str, List[Any]])
def object_from_module(mod: ModuleType, pred: Callable[[Any], bool], desc: str) -> Do:
    all = yield objects_from_module(mod, pred)
    yield all.head.to_either(f'no {desc} in `{mod.__name__}.__all__`')


AS = TypeVar('AS')
A = TypeVar('A', bound=AS)


def cls_from_module(mod: ModuleType, tpe: Type[AS]) -> Either[str, Type[A]]:
    pred = lambda a: isinstance(a, type) and issubclass(a, tpe)
    return object_from_module(mod, pred, f'subclass of `{tpe}`')


def instances_from_module(mod: ModuleType, tpe: Type[A]) -> Either[str, List[A]]:
    pred = lambda a: isinstance(a, tpe)
    return objects_from_module(mod, pred)


def instance_from_module(mod: ModuleType, tpe: Type[A]) -> Either[str, A]:
    pred = lambda a: isinstance(a, tpe)
    return object_from_module(mod, pred, f'instance of `{tpe.__name__}`')


__all__ = ('object_from_module', 'cls_from_module', 'instance_from_module', 'instances_from_module',)
