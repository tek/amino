from amino.test.spec_spec import Spec
from amino.json import decode_json, dump_json
from amino.dat import Dat
from amino import Right


class E(Dat['E']):

    def __init__(self, a: int, b: str) -> None:
        self.a = a
        self.b = b


class D(Dat['D']):

    def __init__(self, e: E, a: int, b: str) -> None:
        self.e = e
        self.a = a
        self.b = b


class JsonSpec(Spec):

    def codec_dat(self) -> None:
        mod = 'unit.json_spec'
        t = "__type__"
        target = D(E(2, 'E'), 1, 'D')
        json = f'{{"e": {{"a": 2, "b": "E", "{t}": "{mod}.E"}}, "a": 1, "b": "D", "{t}": "{mod}.D"}}'
        decoded = decode_json(json)
        decoded.should.equal(Right(target))
        dump_json(target).should.equal(Right(json))

__all__ = ('JsonSpec',)
