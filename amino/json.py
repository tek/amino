import abc
import json
from typing import TypeVar, Union, Generator, Any, Type, Generic
from numbers import Number

from amino.tc.base import TypeClass
from amino import Either, Left, Map, Try, List, L, _, Right
from amino.do import tdo
from amino.util.string import ToStr

A = TypeVar('A')


class JsonError(ToStr):

    def __init__(self, data: str, error: Union[str, Exception]) -> None:
        self.data = data
        self.error = error

    def _arg_desc(self) -> List[str]:
        return List(self.data, str(self.error))


class Json(Generic[A], ToStr):

    def __init__(self, data: A) -> None:
        self.data = data

    @abc.abstractproperty
    def native(self) -> Union[dict, list, str, Number, None]:
        ...

    def _arg_desc(self) -> List[str]:
        return List(str(self.data))


class JsonObject(Json[Map[str, Json]]):

    @property
    def native(self) -> Union[dict, list, str, Number, None]:
        return self.data.valmap(_.native)


class JsonArray(Json[List[Json]]):

    @property
    def native(self) -> Union[dict, list, str, Number, None]:
        return self.data.map(_.native)


class JsonScalar(Json[Union[str, Number, None]]):

    @property
    def native(self) -> Union[dict, list, str, Number, None]:
        return self.data


class Encoder(Generic[A], TypeClass):

    @abc.abstractmethod
    def encode(self, a: A) -> Either[JsonError, Json]:
        ...


class Decoder(Generic[A], TypeClass):

    @abc.abstractmethod
    def decode(self, tpe: Type[A], data: Map[str, Any]) -> Either[JsonError, A]:
        ...


@tdo(Either[JsonError, Json])
def encode_json(data: A) -> Generator:
    enc = yield Encoder.e_for(data).lmap(L(JsonError)(data, _))
    yield enc.encode(data)


def dump_json(data: A) -> Either[JsonError, str]:
    return encode_json(data) / _.native / json.dumps


@tdo(Either[str, A])
def decode_json_object(data: dict) -> Generator:
    m = Map(data)
    tpe_s = yield m.get('__type__').to_either(f'no `__type__` attr in json object {m}')
    tpe = yield Either.import_path(tpe_s)
    dec = yield Decoder.e(tpe)
    yield dec.decode(tpe, m)


def decode_json(data: str) -> Either[JsonError, A]:
    def object_hook(a: dict) -> A:
        return decode_json_object(a).get_or_raise
    return Try(json.loads, data, object_hook=object_hook).lmap(lambda err: f'decoding json `{data}`: {err}')


class ScalarEncoder(Encoder[Union[Number, str, None]], pred=L(issubclass)(_, (Number, str, type(None)))):

    def encode(self, a: Union[Number, str, None]) -> Either[JsonError, Json]:
        return Right(JsonScalar(a))

__all__ = ('Encoder', 'Decoder')
