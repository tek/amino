import abc
from typing import Any, Callable, TypeVar, Type, Generic

from amino.test.spec_spec import Spec
from amino.dat import Dat
from amino import Right, Maybe, List, Either, Left, do, Do, ADT
from amino.json import dump_json, decode_json
from amino.json.data import JsonError, tpe_key

A = TypeVar('A')


@do(Either[JsonError, A])
def _code_json(a: A) -> Do:
    json = yield dump_json(a)
    yield decode_json(json)


class E(Dat['E']):

    def __init__(self, a: int, b: str) -> None:
        self.a = a
        self.b = b


class D(Dat['D']):

    def __init__(self, e: E, a: int, b: str) -> None:
        self.e = e
        self.a = a
        self.b = b


class M(Dat['M']):

    def __init__(self, a: Maybe[int]) -> None:
        self.a = a


class Li(Dat['Li']):

    def __init__(self, a: List[Any]) -> None:
        self.a = a


class Ei(Dat['Ei']):

    def __init__(self, a: Either[str, E], b: Either[str, List[int]], c: Either[str, E]) -> None:
        self.a = a
        self.b = b
        self.c = c


def encode_me() -> int:
    return 5


class Fun(Dat['Fun']):

    def __init__(self, f: Callable[[], int]) -> None:
        self.f = f


mod = 'unit.json_spec'


class Tpe(Dat['Tpe']):

    def __init__(self, tpe: Type[A], none: type) -> None:
        self.tpe = tpe
        self.none = none


class _Abstr(ADT['_Abstr']):

    @abc.abstractmethod
    def abs(self, a: int) -> None:
        ...


class _Sub1(_Abstr):

    def __init__(self, a: int) -> None:
        self.a = a

    def abs(self, a: int) -> None:
        pass


class _Cont(Dat['_Cont']):

    def __init__(self, a: _Abstr) -> None:
        self.a = a


Ab = TypeVar('Ab', bound=_Abstr)


class TV(Generic[Ab], Dat['Ab']):

    def __init__(self, a: Ab) -> None:
        self.a = a


class JsonSpec(Spec):

    def codec_dat(self) -> None:
        target = D(E(2, 'E'), 1, 'D')
        json = f'{{"e": {{"a": 2, "b": "E", "{tpe_key}": "{mod}.E"}}, "a": 1, "b": "D", "{tpe_key}": "{mod}.D"}}'
        decoded = decode_json(json)
        decoded.should.equal(Right(target))
        dump_json(target).should.equal(Right(json))

    def codec_maybe(self) -> None:
        json = f'{{"a": null, "{tpe_key}": "{mod}.M"}}'
        decoded = decode_json(json)
        (decoded // dump_json).should.equal(Right(json))

    def codec_list(self) -> None:
        json = f'{{"a": [1, 2, "string"], "{tpe_key}": "{mod}.Li"}}'
        decoded = decode_json(json)
        (decoded // dump_json).should.equal(Right(json))

    def codec_either(self) -> None:
        v = Ei(Right(E(7, 'value')), Right(List(5, 9)), Left('error'))
        json = dump_json(v)
        (json // decode_json).should.equal(Right(v))

    def function(self) -> None:
        @do(Either[str, int])
        def run() -> Do:
            decoded = yield _code_json(Fun(encode_me))
            return decoded.f()
        run().should.equal(Right(5))

    def tuple(self) -> None:
        t = (4, 5, 6)
        _code_json(t).should.equal(Right(t))

    def tpe(self) -> None:
        t = Tpe(Tpe, type(None))
        _code_json(t).should.equal(Right(t))

    def adt(self) -> None:
        a = _Cont(_Sub1(1))
        _code_json(a).should.equal(Right(a))

    def type_var(self) -> None:
        a = TV(_Sub1(1))
        _code_json(a).should.equal(Right(a))

__all__ = ('JsonSpec',)
