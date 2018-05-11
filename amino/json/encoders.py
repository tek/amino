from typing import Union, TypeVar, Mapping, Any, List as TList, Callable, Tuple, Type
from numbers import Number
from uuid import UUID
from types import FunctionType

from amino import Either, List, L, _, Right, Lists, Maybe, Path, Map, Boolean, do, Do, Try, Dat
from amino.json.encoder import Encoder, encode_json, json_object_with_type
from amino.json.data import JsonError, Json, JsonArray, JsonScalar, JsonObject, JsonNull

A = TypeVar('A')
B = TypeVar('B')
Sub = TypeVar('Sub', bound=Dat)


class ScalarEncoder(Encoder[Union[Number, str, None]], pred=L(issubclass)(_, (Number, str, type(None)))):

    def encode(self, a: Union[Number, str, None]) -> Either[JsonError, Json]:
        return Right(JsonScalar(a))


class MapEncoder(Encoder[List], pred=L(issubclass)(_, Mapping)):

    def encode(self, a: Map[str, Any]) -> Either[JsonError, Json]:
        return Map(a).traverse(encode_json, Either) / JsonObject


class ListEncoder(Encoder[List], pred=L(issubclass)(_, TList)):

    def encode(self, a: TList) -> Either[JsonError, Json]:
        return Lists.wrap(a).traverse(encode_json, Either) / JsonArray


class MaybeEncoder(Encoder[Maybe], tpe=Maybe):

    def encode(self, a: Maybe[A]) -> Either[JsonError, Json]:
        return a.map(encode_json) | (lambda: Right(JsonNull.cons()))


class EitherEncoder(Encoder[Either], tpe=Either):

    @do(Either[JsonError, Json])
    def encode(self, a: Either[B, A]) -> Do:
        json = yield encode_json(a.value)
        yield Right(json_object_with_type(Map(value=json), type(a)))


class UUIDEncoder(Encoder[UUID], tpe=UUID):

    def encode(self, a: UUID) -> Either[JsonError, Json]:
        return Right(JsonScalar(str(a)))


class PathEncoder(Encoder[Path], tpe=Path):

    def encode(self, a: Path) -> Either[JsonError, Json]:
        return Right(JsonScalar(str(a)))


class BooleanEncoder(Encoder[Boolean], tpe=Boolean):

    def encode(self, a: Boolean) -> Either[JsonError, Json]:
        return Right(JsonScalar(a.value))


@do(Either[JsonError, Json])
def encode_instance(a: A, tpe: type, module: str, names: list) -> Do:
    mod_json = yield encode_json(module)
    names_json = yield encode_json(names)
    return json_object_with_type(Map(module=mod_json, names=names_json), tpe)


@do(Either[JsonError, Json])
def encode_instance_simple(data: A, tpe: type) -> Do:
    mod = yield Try(lambda: data.__module__)
    names = yield Try(lambda: data.__qualname__.split('.'))
    yield encode_instance(data, tpe, mod, names)


class FunctionEncoder(Encoder[Callable], tpe=FunctionType):

    @do(Either[JsonError, Json])
    def encode(self, data: Callable) -> Do:
        yield encode_instance_simple(data, Callable)


class TupleEncoder(Encoder[Tuple], tpe=tuple):

    @do(Either[JsonError, Json])
    def encode(self, data: Tuple) -> Do:
        array = yield encode_json(Lists.wrap(data))
        return json_object_with_type(Map(data=array), tuple)


class TypeEncoder(Encoder[Type], tpe=type):

    def encode(self, data: Type) -> Either[JsonError, Json]:
        return encode_instance_simple(data, Type)


class DatEncoder(Encoder, tpe=Dat):

    @do(Either[JsonError, Map])
    def encode(self, a: Sub) -> Do:
        jsons = yield a._dat__values.traverse(encode_json, Either)
        yield Right(json_object_with_type(Map(a._dat__names.zip(jsons)), type(a)))


__all__ = ('ListEncoder', 'ScalarEncoder', 'MaybeEncoder', 'UUIDEncoder', 'PathEncoder', 'MapEncoder', 'EitherEncoder',
           'BooleanEncoder', 'encode_instance', 'FunctionEncoder', 'TupleEncoder', 'TypeEncoder', 'DatEncoder',)
