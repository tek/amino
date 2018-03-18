from typing import Type, TypeVar, Collection, Mapping
from numbers import Number
from uuid import UUID

from amino.json.decoder import Decoder, decode, decode_json_type_json
from amino import Maybe, Either, List, Lists, Left, Boolean, Try, Map, Right, Nothing, Just, Path, do, Do, _, L
from amino.json.data import JsonError, Json, JsonObject

A = TypeVar('A')
B = TypeVar('B')


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
            inner.cata(
                lambda a: decode_json_type_json(data, a) / Just,
                lambda: data.scalar.e(f'invalid type for `Maybe`: {data}', Maybe.check(data.data))
            )
        )


@do(Either[JsonError, Either[A, B]])
def either_from_object(data: JsonObject, ltype: Type[A], rtype: Type[B]) -> Do:
    value = yield data.field('value')
    decoded = yield decode(value)
    tpe = yield data.tpe
    yield Right(tpe(decoded))


class EitherDecoder(Decoder, tpe=Either):

    @do(Either[JsonError, Either[A, B]])
    def decode(self, tpe: Type[Either], data: Json) -> Do:
        err = JsonError(data, f'too few types in Either')
        ltype, rtype = yield Lists.wrap(tpe.__args__).lift_all(0, 1).to_either(err)
        yield (
            either_from_object(data, ltype, rtype)
            if data.object else
            Left(JsonError(data, f'invalid type for `Either`'))
        )


class BooleanDecoder(Decoder, tpe=Boolean):

    def decode(self, tpe: Type[Boolean], data: Json) -> Either[JsonError, Boolean]:
        return data.scalar.e(f'invalid type for `Boolean`: {data}', Boolean(data.data))


class UUIDDecoder(Decoder, tpe=UUID):

    def decode(self, tpe: Type[UUID], data: Json) -> Either[JsonError, UUID]:
        return data.scalar.flat_e(f'invalid type for `UUID`: {data}', Try(UUID, data.data))


class PathDecoder(Decoder, tpe=Path):

    def decode(self, tpe: Type[Path], data: Json) -> Either[JsonError, Path]:
        return data.scalar.flat_e(f'invalid type for `Path`: {data}', Try(Path, data.data))


__all__ = ('MaybeDecoder', 'StringDecoder', 'NumberDecoder', 'ListDecoder', 'BooleanDecoder', 'MapDecoder',
           'PathDecoder')
