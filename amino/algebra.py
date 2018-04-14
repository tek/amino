import typing
from typing import GenericMeta, Any
from types import SimpleNamespace

from amino import List, Lists, Nil, Maybe
from amino.util.string import ToStr


def is_algebra(bases: List[type]) -> bool:
    return bases.exists(lambda a: hasattr(a, '__algebra_base__'))


def find_algebra(name: str, bases: List[type]) -> Maybe[type]:
    return bases.find(lambda a: hasattr(a, '__algebra_variants__'))


def setup_algebra(name: str, inst: type, bases: List[type]) -> None:
    if is_algebra(bases):
        inst.__algebra_variants__ = List()
    else:
        raise Exception(f'algebra subclass has no algebra superclass: {name}')


def setup_variant(name: str, inst: type, bases: List[type], algebra: type) -> None:
    inst.__algebra_index__ = len(algebra.__algebra_variants__)
    algebra.__algebra_variants__.append(inst)


def setup_algebraic_type(name: str, inst: type, bases: List[type]) -> None:
    return (
        find_algebra(name, bases)
        .cata_f(
            lambda a: setup_variant(name, inst, bases, a),
            lambda: setup_algebra(name, inst, bases)
        )
    )


class AlgebraMeta(GenericMeta):

    def __new__(
            cls,
            name: str,
            bases: typing.List[type],
            namespace: SimpleNamespace,
            algebra_base: bool=False,
            **kw: Any,
    ) -> None:
        inst = super().__new__(cls, name, bases, namespace, **kw)
        if inst.__args__ is None:
            if algebra_base:
                inst.__algebra_base__ = None
            else:
                setup_algebraic_type(name, inst, Lists.wrap(bases))
        return inst


class Algebra(ToStr, metaclass=AlgebraMeta, algebra_base=True):
    pass


__all__ = ('AlgebraMeta', 'Algebra')
