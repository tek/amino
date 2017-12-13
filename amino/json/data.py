import abc
from typing import TypeVar, Union, Generic, Generator
from numbers import Number

from amino import Map, List, _, Either, Right, Left, Boolean
from amino.util.string import ToStr
from amino.algebra import Algebra
from amino.do import tdo

A = TypeVar('A')


class JsonError(ToStr):

    def __init__(self, data: str, error: Union[str, Exception]) -> None:
        self.data = data
        self.error = error

    def _arg_desc(self) -> List[str]:
        return List(self.data, str(self.error))


class Json(Generic[A], Algebra, base=True):

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

    def error(self, msg: Union[str, Exception]) -> JsonError:
        return JsonError(self.data, msg)


class JsonObject(Json[Map[str, Json]]):

    @property
    def native(self) -> Union[dict, list, str, Number, None]:
        return self.data.valmap(_.native)

    @property
    @tdo(Either[JsonError, type])
    def tpe(self) -> Generator:
        jtpe = yield self.data.lift('__type__').to_either(self.error(f'no `__type__` field in json object'))
        tpe_s = yield (
            Right(jtpe.data)
            if isinstance(jtpe, JsonScalar) else
            Left(self.error('invalid type for `__type__`: {jtpe}'))
        )
        yield Either.import_path(tpe_s).lmap(self.error)

    def field(self, key: str) -> Either[JsonError, Json]:
        return self.data.lift(key).to_either(self.error(f'no field `key`'))


class JsonArray(Json[List[Json]]):

    @property
    def native(self) -> Union[dict, list, str, Number, None]:
        return self.data.map(_.native)

    def field(self, key: str) -> Either[JsonError, Json]:
        return Left(self.error('JsonArray has no fields'))


class JsonScalar(Json[Union[str, Number, None]]):

    @property
    def native(self) -> Union[dict, list, str, Number, None]:
        return self.data

    def field(self, key: str) -> Either[JsonError, Json]:
        return Left(self.error('JsonScalar has no fields'))

__all__ = ('JsonError', 'Json', 'JsonObject', 'JsonArray', 'JsonScalar')
