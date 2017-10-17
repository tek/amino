from typing import Any

from amino.test.spec_spec import Spec
from amino.dat import Dat
from amino import Right, Maybe, List
from amino.json.decoder import decode_json
from amino.json.encoder import dump_json


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


mod = 'unit.json_spec'


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

__all__ = ('JsonSpec',)
