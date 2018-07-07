import abc
from typing import TypeVar, Union, Generic
from numbers import Number

from amino import Map, List, _, Either, Right, Left, Boolean
from amino.util.string import ToStr
from amino.algebra import Algebra

A = TypeVar('A')
tpe_key = '__type__'


class JsonError(ToStr):

    def __init__(self, data: Union['Json', str], error: Union[str, Exception]) -> None:
        self.data = data
        self.error = error

    def _arg_desc(self) -> List[str]:
        return List(self.data, str(self.error))

    @property
    def exception(self) -> Exception:
        return self.error if isinstance(self.error, Exception) else Exception(self.error)


class Json(Algebra[A]):

    def __init__(self, data: A) -> None:
        self.data = data

    @abc.abstractproperty
    def native(self) -> Union[dict, list, str, Number, None]:
        ...

    @abc.abstractmethod
    def field(self, key: str) -> Either[JsonError, 'Json']:
        ...

    def _arg_desc(self) -> List[str]:
        return List(str(self.data))

    @property
    def scalar(self) -> Boolean:
        return Boolean.isinstance(self, JsonScalar)

    @property
    def array(self) -> Boolean:
        return Boolean.isinstance(self, JsonArray)

    @property
    def object(self) -> Boolean:
        return Boolean.isinstance(self, JsonObject)

    @property
    def absent(self) -> Boolean:
        return Boolean.isinstance(self, JsonAbsent)

    @property
    def null(self) -> Boolean:
        return Boolean.isinstance(self, JsonNull)

    def error(self, msg: Union[str, Exception]) -> JsonError:
        return JsonError(self.data, msg)

    @property
    def as_scalar(self) -> Either[JsonError, 'JsonScalar']:
        return Right(self) if self.scalar else Left(self.error('not a scalar'))

    @property
    def as_array(self) -> Either[JsonError, 'JsonArray']:
        return Right(self) if self.array else Left(self.error('not an array'))

    @property
    def as_object(self) -> Either[JsonError, 'JsonObject']:
        return Right(self) if self.object else Left(self.error('not an object'))


class JsonObject(Json[Map[str, Json]]):

    @property
    def native(self) -> Union[dict, list, str, Number, None]:
        return self.data.valmap(_.native)

    def field(self, key: str) -> Either[JsonError, Json]:
        return Right(self.data.lift(key) | JsonAbsent(self.error(f'no field `{key}`')))

    @property
    def has_type(self) -> Boolean:
        return self.data.contains(tpe_key)


class JsonArray(Json[List[Json]]):

    @property
    def native(self) -> Union[dict, list, str, Number, None]:
        return self.data.map(_.native)

    def field(self, key: str) -> Either[JsonError, Json]:
        return Left(self.error('JsonArray has no fields'))


class JsonScalar(Json[Union[str, Number]]):

    @property
    def native(self) -> Union[dict, list, str, Number]:
        return self.data

    def field(self, key: str) -> Either[JsonError, Json]:
        return Left(self.error('JsonScalar has no fields'))


class JsonNull(Json[None]):

    @staticmethod
    def cons() -> 'Json[None]':
        return JsonNull(None)

    @property
    def native(self) -> None:
        None

    def field(self, key: str) -> Either[JsonError, Json]:
        return Left(self.error('JsonNull has no fields'))


class JsonAbsent(Json[JsonError]):

    @property
    def native(self) -> Union[dict, list, str, Number, None]:
        return None

    def field(self, key: str) -> Either[JsonError, Json]:
        return Right(self)


__all__ = ('JsonError', 'Json', 'JsonObject', 'JsonArray', 'JsonScalar', 'JsonAbsent')
