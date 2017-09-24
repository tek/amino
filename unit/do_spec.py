from typing import Generator, Any

from amino.test.spec_spec import Spec

from kallikrein import kf, Expectation, k
from kallikrein.matchers.maybe import be_just, be_nothing
from amino import Just, Nothing, Maybe, do, Eval
from amino.state import EvalState, StateT


class DoSpec(Spec):
    '''do notation
    yield all `Just`s $just
    yield a `Nothing` $nothing
    `EvalState` $eval_state
    '''

    def just(self) -> Expectation:
        @do
        def run(i: int) -> Generator[Maybe[int], Any, None]:
            a = yield Just(i)
            b = yield Just(a + 5)
            c = yield Just(b + 7)
            d = yield Just(c * 3)
            yield Just(d)
        return kf(run, 3).must(be_just(45))

    def nothing(self) -> None:
        @do
        def run(i: int) -> Generator[Maybe[int], Any, None]:
            yield Just(i)
            b = yield Nothing
            c = yield Just(b + 7)
            yield Just(c)
        return kf(run, 3).must(be_nothing)

    def eval_state(self) -> None:
        @do
        def run() -> Generator[StateT[Eval, str, Any], Any, None]:
            a = yield EvalState.pure(1)
            yield EvalState.set('state')
            yield EvalState.inspect(lambda s: f'{s}: {a}')
        return k(run().run_a('init').value) == 'state: 1'

__all__ = ('DoSpec',)
