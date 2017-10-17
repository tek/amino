from typing import Type
from numbers import Number

from amino.json.decoder import Decoder
from amino import Maybe, Either
from amino.json.data import JsonError, Json


class StringDecoder(Decoder, tpe=str):

    def decode(self, tpe: Type[str], data: Json) -> Either[JsonError, str]:
        return data.scalar.e(f'invalid type for `str`: {data}', data.data)


class NumberDecoder(Decoder, sub=Number):

    def decode(self, tpe: Type[int], data: Json) -> Either[JsonError, int]:
        return data.scalar.e(f'invalid type for `int`: {data}', data.data)


class MaybeDecoder(Decoder, tpe=Maybe):

    def decode(self, tpe: Type[Maybe], data: Json) -> Either[JsonError, Maybe]:
        return data.scalar.e(f'invalid type for `Maybe`: {data}', Maybe.check(data.data))

__all__ = ('MaybeDecoder',)
