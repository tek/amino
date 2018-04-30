import abc
import json
from typing import TypeVar, Generic, Type

from amino.tc.base import TypeClass
from amino import Either, L, _, Map, do, Do
from amino.json.data import JsonError, Json, JsonObject, JsonScalar

A = TypeVar('A')


class Encoder(Generic[A], TypeClass):

    @abc.abstractmethod
    def encode(self, a: A) -> Either[JsonError, Json]:
        ...


@do(Either[JsonError, Json])
def encode_json(data: A) -> Do:
    enc = yield Encoder.e_for(data).lmap(L(JsonError)(data, _))
    yield enc.encode(data)


@do(Either[JsonError, str])
def dump_json(data: A) -> Do:
    js = yield encode_json(data)
    return json.dumps(js.native)


def json_type(tpe: Type) -> Json:
    mod = '__builtins__' if tpe.__module__ == 'builtins' else tpe.__module__
    return JsonScalar(f'{mod}.{tpe.__name__}')


def json_object_with_type(fields: Map[str, JsonObject], tpe: Type[A]) -> Json:
    return JsonObject(fields.cat(('__type__', json_type(tpe))))


__all__ = ('Encoder', 'encode_json', 'dump_json')
