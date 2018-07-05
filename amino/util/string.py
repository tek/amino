import re
import abc
from typing import Any, Sized
from functools import singledispatch

import amino


def snake_case(name: str) -> str:
    s1 = re.sub('([^_])([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


@singledispatch
def decode(value: Any) -> Any:
    return value


@decode.register(bytes)
def decode_bytes(value: bytes) -> str:
    return value.decode()


@decode.register(list)
def decode_list(value: list) -> 'amino.List[str]':
    return amino.List.wrap(value).map(decode)


@decode.register(tuple)
def decode_tuple(value: tuple) -> 'amino.List[str]':
    return decode_list(value)


@decode.register(dict)
def decode_dict(value: dict) -> 'amino.Map[str, str]':
    return amino.Map.wrap(value).keymap(decode).valmap(decode)


@decode.register(Exception)
def decode_exc(value: Exception) -> str:
    return decode_list(value.args).head | str(value)


def camelcase(name: str, sep: str='', splitter: str='_') -> str:
    return sep.join([n.capitalize() for n in re.split(splitter, name)])

camelcaseify = camelcase


def safe_string(value: Any) -> str:
    try:
        return str(value)
    except Exception:
        try:
            return repr(value)
        except Exception:
            return 'invalid'


class ToStr(abc.ABC):

    @abc.abstractmethod
    def _arg_desc(self) -> 'amino.List[str]':
        ...

    def __str__(self) -> str:
        args = self._arg_desc().join_comma
        return f'{self.__class__.__name__}({args})'

    def __repr__(self) -> str:
        return str(self)


def plural_s(items: Sized) -> str:
    return '' if len(items) == 1 else 's'


def indent(data: str, count: int=2) -> str:
    ws = ' ' * count
    return f'{ws}{data}'


__all__ = ('snake_case', 'decode', 'camelcaseify', 'camelcase', 'plural_s', 'indent',)
