from typing import Any, Callable, TypeVar

from amino.test.spec_spec import Spec
from amino.dat import Dat
from amino import Right, Maybe, List, Either, Left, do, Do
from amino.json import dump_json, decode_json
from amino.json.data import JsonError


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

A = TypeVar('A')


@do(Either[JsonError, A])
def code_json(a: A) -> Do:
    json = yield dump_json(a)
    yield decode_json(json)


class JsonSpec(Spec):

    def codec_dat(self) -> None:
        t = "__type__"
        target = D(E(2, 'E'), 1, 'D')
        json = f'{{"e": {{"a": 2, "b": "E", "{t}": "{mod}.E"}}, "a": 1, "b": "D", "{t}": "{mod}.D"}}'
        decoded = decode_json(json)
        decoded.should.equal(Right(target))
        dump_json(target).should.equal(Right(json))

    def codec_maybe(self) -> None:
        json = f'{{"a": null, "__type__": "{mod}.M"}}'
        decoded = decode_json(json)
        (decoded // dump_json).should.equal(Right(json))

    def codec_list(self) -> None:
        json = f'{{"a": [1, 2, "string"], "__type__": "{mod}.Li"}}'
        decoded = decode_json(json)
        (decoded // dump_json).should.equal(Right(json))

    def codec_either(self) -> None:
        v = Ei(Right(E(7, 'value')), Right(List(5, 9)), Left('error'))
        json = dump_json(v)
        (json // decode_json).should.equal(Right(v))

    def function(self) -> None:
        @do(Either[str, int])
        def run() -> Do:
            decoded = yield code_json(Fun(encode_me))
            return decoded.f()
        run().should.equal(Right(5))

    def tuple(self) -> None:
        t = (4, 5, 6)
        code_json(t).should.equal(Right(t))

__all__ = ('JsonSpec',)
