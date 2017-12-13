import abc
import json
from typing import TypeVar, Generator, Generic, Type

from amino.tc.base import TypeClass
from amino import Either, L, _, Map
from amino.do import tdo
from amino.json.data import JsonError, Json, JsonObject, JsonScalar
from amino.util.tpe import qualified_type

A = TypeVar('A')


class Encoder(Generic[A], TypeClass):

    @abc.abstractmethod
    def encode(self, a: A) -> Either[JsonError, Json]:
        ...


@tdo(Either[JsonError, Json])
def encode_json(data: A) -> Generator:
    enc = yield Encoder.e_for(data).lmap(L(JsonError)(data, _))
    yield enc.encode(data)


def dump_json(data: A) -> Either[JsonError, str]:
    return encode_json(data) / _.native / json.dumps


def json_object_with_type(fields: Map[str, JsonObject], tpe: Type[A]) -> Json:
    return JsonObject(fields.cat(('__type__', JsonScalar(qualified_type(tpe)))))

__all__ = ('Encoder', 'encode_json', 'dump_json')
