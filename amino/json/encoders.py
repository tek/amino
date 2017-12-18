from typing import Union, Collection, TypeVar, Mapping, Any, List as TList
from numbers import Number
from uuid import UUID

from amino import Either, List, L, _, Right, Lists, Maybe, Path, Map, Boolean, do, Do
from amino.json.encoder import Encoder, encode_json, json_object_with_type
from amino.json.data import JsonError, Json, JsonArray, JsonScalar, JsonObject

A = TypeVar('A')
B = TypeVar('B')


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
        return Right(JsonScalar(a | None))


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


class TypeEncoder(Encoder[type], tpe=type):

    def encode(self, a: type) -> Either[JsonError, Json]:
        return Right(json_object_with_type(Map(), a))


class BooleanEncoder(Encoder[Boolean], tpe=Boolean):

    def encode(self, a: Boolean) -> Either[JsonError, Json]:
        return Right(JsonScalar(a.value))


__all__ = ('ListEncoder', 'ScalarEncoder', 'MaybeEncoder', 'UUIDEncoder', 'PathEncoder', 'TypeEncoder', 'MapEncoder')
