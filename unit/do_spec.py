from typing import Generator, Any

from amino.test.spec_spec import Spec

from amino import Just, Nothing, Maybe, do, Eval
from amino.state import EvalState, StateT


class DoSpec(Spec):

    def just(self) -> None:
        @do
        def run(i: int) -> Generator[Maybe[int], Any, None]:
            a = yield Just(i)
            b = yield Just(a + 5)
            c = yield Just(b + 7)
            d = yield Just(c * 3)
            yield Just(d)
        run(3).should.equal(Just(45))

    def nothing(self) -> None:
        @do
        def run(i: int) -> Generator[Maybe[int], Any, None]:
            yield Just(i)
            b = yield Nothing
            c = yield Just(b + 7)
            yield Just(c)
        run(3).should.equal(Nothing)

    def eval_state(self) -> None:
        @do
        def run() -> Generator[StateT[Eval, str, Any], Any, None]:
            a = yield EvalState.pure(1)
            yield EvalState.set('state')
            yield EvalState.inspect(lambda s: f'{s}: {a}')
        run().run_a('init').value.should.equal('state: 1')

__all__ = ('DoSpec',)
