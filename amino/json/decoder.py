import abc
from typing import TypeVar, Type, Generic

from amino.tc.base import TypeClass
from amino import Either, Map, Right, Lists, Do, _, L, Left
from amino.do import do
from amino.json.data import JsonError, JsonObject, JsonArray, JsonScalar, Json, JsonAbsent
from amino.json.parse import parse_json
from amino.dispatch import dispatch_alg

A = TypeVar('A')


class Decoder(Generic[A], TypeClass):

    @abc.abstractmethod
    def decode(self, tpe: Type[A], data: Json) -> Either[JsonError, A]:
        ...


@do(Either[str, A])
def decode_json_object(data: dict) -> Do:
    m = Map(data)
    tpe_s = yield m.get('__type__').to_either(f'no `__type__` attr in json object {m}')
    tpe = yield Either.import_path(tpe_s)
    dec = yield Decoder.e(tpe)
    yield dec.decode(tpe, m)


class Decode:

    @do(Either[JsonError, A])
    def decode_json_object(self, json: JsonObject) -> Do:
        tpe = yield json.tpe
        dec = yield Decoder.e(tpe).lmap(L(JsonError)(json, _))
        yield dec.decode(tpe, json)

    def decode_json_array(self, json: JsonArray) -> Either[JsonError, A]:
        return Lists.wrap(json.data).traverse(decode, Either)

    def decode_json_scalar(self, json: JsonScalar) -> Either[JsonError, A]:
        return Right(json.data)

    def decode_json_absent(self, json: JsonAbsent) -> Either[JsonError, A]:
        return Left(json.data)


decode = dispatch_alg(Decode(), Json, 'decode_')


@do(Either[JsonError, A])
def decode_json(data: str) -> Do:
    json = yield parse_json(data).lmap(lambda e: JsonError(data, e))
    yield decode(json)


@do(Either[JsonError, A])
def decode_json_type_json(json: Json, tpe: Type[A]) -> Do:
    dec = yield Decoder.e(tpe).lmap(L(JsonError)(json, _))
    yield dec.decode(tpe, json)


@do(Either[JsonError, A])
def decode_json_type(data: str, tpe: Type[A]) -> Do:
    json = yield parse_json(data).lmap(lambda e: JsonError(data, e))
    yield decode_json_type_json(json, tpe)


__all__ = ('Decoder', 'decode_json_object', 'decode_json', 'decode', 'decode_json_type', 'decode_json_type_json')
