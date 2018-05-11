import abc
from typing import TypeVar, Type, Generic

from amino.tc.base import TypeClass
from amino import Either, Map, Right, Lists, Do, _, L, Left, Dat, List, Maybe
from amino.do import do
from amino.json.data import JsonError, JsonObject, JsonArray, JsonScalar, Json, JsonAbsent, JsonNull, tpe_key
from amino.json.parse import parse_json
from amino.case import Case
from amino.logging import module_log

A = TypeVar('A')
log = module_log()


class TypeInfo(Dat['TypeInfo']):

    def __init__(self, module: str, names: List[str]) -> None:
        self.module = module
        self.names = names


class Decoder(Generic[A], TypeClass):

    @abc.abstractmethod
    def decode(self, tpe: Type[A], data: Json) -> Either[JsonError, A]:
        ...


@do(Either[str, A])
def decode_json_object(data: dict) -> Do:
    m = Map(data)
    tpe_s = yield m.lift(tpe_key).to_either(f'no `{tpe_key}` attr in json object {m}')
    tpe = yield Either.import_path(tpe_s)
    dec = yield Decoder.e(tpe)
    yield dec.decode(tpe, m)


@do(Either[str, type])
def builtin_type(type_info: TypeInfo) -> Do:
    name = yield type_info.names.head.to_either(f'no name specified for builtin type')
    yield (
        Right(type(None))
        if name == 'NoneType' else
        Maybe.optional(__builtins__.get(name)).to_either(f'no builtin type named `{name}`')
    )


@do(Either[str, type])
def select_type(type_info: TypeInfo) -> Do:
    mod = yield Either.import_module(type_info.module)
    yield type_info.names.fold_m(Right(mod))(Either.getattr)


def decode_type_info(json: Json) -> Either[JsonError, TypeInfo]:
    return decode_json_type_json(json, TypeInfo)


@do(Either[JsonError, type])
def type_info(json: JsonObject) -> Do:
    jtpe = yield json.data.lift(tpe_key).to_either(json.error(f'no `{tpe_key}` field in json object'))
    type_info = yield decode_type_info(jtpe)
    yield (
        builtin_type(type_info)
        if type_info.module == '__builtins__' else
        select_type(type_info)
    ).lmap(json.error)


class decode(Generic[A], Case[Json, Either[JsonError, A]], alg=Json):

    @do(Either[JsonError, A])
    def decode_json_object(self, json: JsonObject) -> Do:
        tpe = yield type_info(json)
        dec = yield Decoder.e(tpe).lmap(L(JsonError)(json, _))
        yield dec.decode(tpe, json)

    def decode_json_array(self, json: JsonArray) -> Either[JsonError, A]:
        return Lists.wrap(json.data).traverse(self, Either)

    def decode_json_scalar(self, json: JsonScalar) -> Either[JsonError, A]:
        return Right(json.data)

    def decode_json_null(self, json: JsonNull) -> Either[JsonError, A]:
        return Right(None)

    def decode_json_absent(self, json: JsonAbsent) -> Either[JsonError, A]:
        return Left(JsonError(json.data), 'json absent')


@do(Either[JsonError, A])
def decode_json(data: str) -> Do:
    json = yield parse_json(data)
    yield decode.match(json)


@do(Either[JsonError, A])
def decode_json_type_json(json: Json, tpe: Type[A]) -> Do:
    dec = yield Decoder.e(tpe).lmap(L(JsonError)(json, _))
    yield dec.decode(tpe, json)


@do(Either[JsonError, A])
def decode_json_type(data: str, tpe: Type[A]) -> Do:
    json = yield parse_json(data)
    yield decode_json_type_json(json, tpe)


__all__ = ('Decoder', 'decode_json_object', 'decode_json', 'decode', 'decode_json_type', 'decode_json_type_json')
