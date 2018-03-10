import inspect
from typing import TypeVar, Type, Any, Generic, cast, Tuple

from amino import Map, Lists, List, Nil, _, Either, Right, Maybe, Just, L, do, Do
from amino.util.string import ToStr
from amino.func import Val
from amino.lazy import lazy
from amino.json.decoder import Decoder
from amino.json.data import JsonError, JsonObject
from amino.json.encoder import Encoder, encode_json, json_object_with_type
from amino.algebra import AlgebraMeta, Algebra
from amino.tc.base import ImplicitsMeta
from amino.util.tpe import qualified_type

A = TypeVar('A')


class KeepField:
    pass


class Field(ToStr):

    def __init__(self, name: str, tpe: Type) -> None:
        self.name = name
        self.tpe = tpe

    @property
    def qualified_type(self) -> None:
        return qualified_type(self.tpe)

    def _arg_desc(self) -> List[str]:
        return List(self.name, self.qualified_type)

    @property
    def param_str(self) -> str:
        return f'''{self.name}: '{self.qualified_type}'=Dat.Keep'''


Sub = TypeVar('Sub', bound='Dat')


class FieldMutator(Generic[Sub]):

    def __init__(self, name: str, target: 'Dat[Sub]') -> None:
        self.name = name
        self.target = target


class FieldSetter(Generic[Sub], FieldMutator[Sub]):

    def __call__(self, value) -> Sub:
        return self.target.copy(**{self.name: value})


class FieldModifier(Generic[Sub], FieldMutator[Sub]):

    def __call__(self, f) -> Sub:
        return self.target.copy(**{self.name: f(getattr(self.target, self.name))})


class FieldAppender(Generic[Sub], FieldMutator[Sub]):

    def __call__(self, value) -> Sub:
        return self.target.mod(self.name)(_ + value)


class FieldAppender1(Generic[Sub], FieldMutator[Sub]):

    def __call__(self, value) -> Sub:
        return self.target.mod(self.name)(_ + List(value))


class FieldProxy(Generic[Sub], FieldMutator[Sub]):

    def __init__(self, target: 'Dat', tpe: type) -> None:
        self.target = target
        self.tpe = tpe

    def __getattr__(self, name):
        return self(name)

    def __call__(self, name):
        return self.tpe(name, self.target)


def init_fields(spec: inspect.FullArgSpec) -> List[Field]:
    args = Lists.wrap(spec.args).tail | Nil
    types = Map(spec.annotations)
    def field(name: str) -> Field:
        tpe = types.lift(name) | Val(Any)
        return Field(name, tpe)
    return args / field


class DatMeta(ImplicitsMeta):

    def __new__(cls: type, name: str, bases: tuple, namespace: dict, **kw) -> type:
        fs = Map(namespace).lift('__init__') / inspect.getfullargspec / init_fields | Nil
        inst = super().__new__(cls, name, bases, namespace, **kw)
        if not (fs.empty and hasattr(inst, '_dat__fields_value')):
            inst._dat__fields_value = fs
        return inst

    @property
    def _dat__fields(self) -> List[Field]:
        return self._dat__fields_value

    @property
    def _field_count_min(self) -> int:
        return len(self._dat__fields)

    @property
    def _field_count_max(self) -> Maybe[int]:
        return Just(len(self._dat__fields))


# TODO typecheck ctor args in development
class Dat(Generic[Sub], ToStr, metaclass=DatMeta):
    Keep = KeepField()

    @property
    def _dat__fields(self) -> List[Field]:
        return type(self)._dat__fields

    @lazy
    def _dat__names(self) -> List[str]:
        return self._dat__fields.map(_.name)

    @lazy
    def _dat__values(self) -> List[Any]:
        return (
            self._dat__fields
            .traverse(lambda a: Maybe.getattr(self, a.name), Maybe)
            .get_or_fail(lambda: f'corrupt `Dat`: {type(self)}')
        )

    @lazy
    def _dat__items(self) -> List[Tuple[str, Any]]:
        return self._dat__names.zip(self._dat__values)

    @property
    def to_map(self) -> Map[str, Any]:
        return Map(self._dat__items)

    def copy(self, **kw: Any) -> Sub:
        updates = Map(kw)
        def update(f: Field) -> Any:
            return updates.lift(f.name) | (lambda: getattr(self, f.name))
        updated = self._dat__fields / update  # type: ignore
        return cast(Dat, type(self)(*updated))

    def typed_copy(self, **kw: Any) -> Sub:
        updates = Map(kw)
        def update(f: Field) -> Any:
            return updates.lift(f.name).filter_type(f.tpe) | (lambda: getattr(self, f.name))
        updated = self._dat__fields / update  # type: ignore
        return cast(Dat, type(self)(*updated))

    @property
    def append(self) -> FieldProxy:
        return FieldProxy(self, FieldAppender)

    @property
    def append1(self) -> FieldProxy:
        return FieldProxy(self, FieldAppender1)

    @property
    def mod(self) -> FieldProxy:
        return FieldProxy(self, FieldModifier)

    @property
    def set(self) -> FieldProxy:
        return FieldProxy(self, FieldSetter)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and self._dat__values == other._dat__values

    def __iter__(self) -> iter:
        return iter(self._dat__values)

    def __hash__(self) -> int:
        return hash(self._dat__values)

    def _lens_setattr(self, name, value):
        return self.set(name)(value)

    def _arg_desc(self) -> List[str]:
        return self._dat__values / str


class DatDecoder(Decoder, tpe=Dat):

    def decode(self, tpe: Type[Sub], data: JsonObject) -> Either[JsonError, Sub]:
        @do(Either[JsonError, A])
        def decode_field(field: Field) -> Do:
            value = yield data.field(field.name)
            dec = yield Decoder.e(field.tpe).lmap(L(JsonError)(data, _))
            yield dec.decode(field.tpe, value)
        return tpe._dat__fields.traverse(decode_field, Either).map(lambda a: tpe(*a))


class DatEncoder(Encoder, tpe=Dat):

    @do(Either[JsonError, Map])
    def encode(self, a: Sub) -> Do:
        jsons = yield a._dat__values.traverse(encode_json, Either)
        yield Right(json_object_with_type(Map(a._dat__names.zip(jsons)), type(a)))


class ADTMeta(DatMeta, AlgebraMeta):
    pass


class ADT(Generic[Sub], Dat[Sub], Algebra, metaclass=ADTMeta):
    pass

__all__ = ('Dat', 'ADT')
