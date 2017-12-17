from typing import Type, TypeVar, Collection, Mapping
from numbers import Number
from uuid import UUID

from amino.json.decoder import Decoder, decode, decode_json_type_json
from amino import Maybe, Either, List, Lists, Left, Boolean, Try, Map, Right, Nothing, Just
from amino.json.data import JsonError, Json, JsonObject

A = TypeVar('A')


class StringDecoder(Decoder, tpe=str):

    def decode(self, tpe: Type[str], data: Json) -> Either[JsonError, str]:
        return data.scalar.e(f'invalid type for `str`: {data}', data.data)


class NumberDecoder(Decoder, sub=Number):

    def decode(self, tpe: Type[int], data: Json) -> Either[JsonError, int]:
        return data.scalar.e(f'invalid type for `int`: {data}', data.data)


class MapDecoder(Decoder, sub=Mapping):

    def decode(self, tpe: Type[Mapping], data: Json) -> Either[JsonError, Map[str, A]]:
        def dec() -> Either[JsonError, Map[str, A]]:
            return Map(data.data).traverse(decode, Either)
        return data.object.c(dec, lambda: Left(f'invalid type for `Map`: {data}'))


class ListDecoder(Decoder, sub=Collection):

    def decode(self, tpe: Type[Collection], data: Json) -> Either[JsonError, List[A]]:
        def dec() -> Either[JsonError, List[A]]:
            return Lists.wrap(data.data).traverse(decode, Either)
        return data.array.c(dec, lambda: Left(f'invalid type for `List`: {data}'))


def maybe_from_object(data: JsonObject, inner: Maybe[Type[A]]) -> Either[JsonError, Maybe[A]]:
    return (
        decode(data) / Just
        if data.has_type else
        inner.traverse(lambda a: decode_json_type_json(data, a), Either)
    )


class MaybeDecoder(Decoder, tpe=Maybe):

    def decode(self, tpe: Type[Maybe], data: Json) -> Either[JsonError, Maybe[A]]:
        inner = Lists.wrap(tpe.__args__).head
        return (
            Right(Nothing)
            if data.absent else
            maybe_from_object(data, inner)
            if data.object else
            decode(data) / Just
            if data.array else
            data.scalar.e(f'invalid type for `Maybe`: {data}', Maybe.check(data.data))
        )


class BooleanDecoder(Decoder, tpe=Boolean):

    def decode(self, tpe: Type[Boolean], data: Json) -> Either[JsonError, Boolean]:
        return data.scalar.e(f'invalid type for `Boolean`: {data}', Boolean(data.data))


class UUIDDecoder(Decoder, tpe=UUID):

    def decode(self, tpe: Type[UUID], data: Json) -> Either[JsonError, UUID]:
        return data.scalar.flat_e(f'invalid type for `UUID`: {data}', Try(UUID, data.data))


__all__ = ('MaybeDecoder', 'StringDecoder', 'NumberDecoder', 'ListDecoder', 'BooleanDecoder', 'MapDecoder')
