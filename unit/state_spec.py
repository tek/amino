from typing import Tuple

from amino.state.maybe import MaybeState
from amino import Maybe, Just, Left, Right, Either, Id, List
from amino.state.either import EitherState
from amino.state.eval import EvalState
from amino.state.id import IdState
from amino.test.spec_spec import Spec


class State3Spec(Spec):

    def types(self) -> None:
        s: MaybeState[int, int] = MaybeState.pure(5)
        x: Maybe[Tuple[int, int]] = s.run(2)
        x

    def pure(self) -> None:
        assert(MaybeState.s(str).pure(1).run('state') == Just(('state', 1)))

    def flat_map(self) -> None:
        s = MaybeState.s(str).pure(1)
        def f(a: int) -> MaybeState[str, int]:
            return MaybeState.s(str).inspect(lambda s: len(s) + a)
        s1 = s.flat_map(f)
        assert(s1.run('str') == Just(('str', 4)))

    def modify(self) -> None:
        MaybeState.s(str).modify((lambda s: s + ' updated')).run_s('state').should.equal(Just('state updated'))

    def modify_f(self) -> None:
        MaybeState.s(str).modify_f((lambda s: Just(s + ' updated'))).run_s('state').should.equal(Just('state updated'))

    def flat_map_f(self) -> None:
        l = Left('boing')
        EitherState.pure(1).flat_map_f(lambda a: l).run('start').should.equal(l)

    def zip(self) -> None:
        EvalState.pure(1).zip(EvalState.pure(2)).run_a(None)._value().should.equal(List(1, 2))

    def eff(self) -> None:
        def f(a: int) -> EvalState[int, Either[str, int]]:
            return EvalState.pure(Right(2))
        s0: EvalState[int, Either[str, int]] = EvalState.s(int).pure(Right(1))
        s0.eff(Either).flat_map(f).value.run(1)._value().should.equal((1, Right(2)))
        assert ((s0 // EvalState.s(int).modify(lambda a: a).replace).eff(Either).flat_map(f).value.run(1)._value() ==
                (1, Right(2)))

    def id(self) -> None:
        s = IdState.s(int).inspect(lambda s0: s0 * 2).flat_map(lambda a: IdState.pure(a + 4))
        s.run(5).should.equal(Id((5, 14)))

    def transform_s(self) -> None:
        def trans_from(r: str) -> int:
            return int(r)
        def trans_to(r: str, s: int) -> str:
            return str(s)
        s1 = IdState(Id(lambda s: Id((s + 1, None)))).transform_s(trans_from, trans_to)
        s1.run_s('2').value.should.equal('3')

    def transform_f(self) -> None:
        MaybeState.pure(7).transform_f(EitherState, lambda m: m.to_either('none')).run_a(None).should.equal(Right(7))

    def lift_left(self) -> None:
        EitherState.lift(Left(1)).run_a(None).should.equal(Left(1))


__all__ = ('State3Spec',)
