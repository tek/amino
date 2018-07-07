from typing import Any

from amino.test.spec_spec import Spec

from amino import Just, Nothing, Maybe, do, Eval, Do, List
from amino.state import EvalState, StateT


class DoSpec(Spec):

    def just(self) -> None:
        @do(Maybe[int])
        def run(i: int) -> Do:
            a = yield Just(i)
            b = yield Just(a + 5)
            c = yield Just(b + 7)
            d = yield Just(c * 3)
            return d
        run(3).should.equal(Just(45))

    def nothing(self) -> None:
        @do(Maybe[int])
        def run(i: int) -> Do:
            yield Just(i)
            b = yield Nothing
            c = yield Just(b + 7)
            yield Just(c)
        run(3).should.equal(Nothing)

    def eval_state(self) -> None:
        @do(StateT[Eval, str, Any])
        def run() -> Do:
            a = yield EvalState.pure(1)
            yield EvalState.set('state')
            yield EvalState.inspect(lambda s: f'{s}: {a}')
        run().run_a('init').value.should.equal('state: 1')


__all__ = ('DoSpec',)
