from amino.state import MaybeState, EitherState, EvalState, IdState, State
from amino.test.spec_spec import Spec
from amino import Just, Left, List, Either, Right, I
from amino.id import Id


class StateSpec(Spec):

    def pure(self) -> None:
        MaybeState.pure(1).run('state').should.equal(Just(('state', 1)))

    def flat_map(self) -> None:
        s = MaybeState.pure(1)
        def f(a: int) -> None:
            return MaybeState.inspect(lambda s: len(s) + a)
        s1 = s.flat_map(f)
        return s1.run('str').should.equal(Just(('str', 4)))

    def modify(self) -> None:
        MaybeState.modify((lambda s: s + ' updated')).run_s('state').should.equal(Just('state updated'))

    def modify_f(self) -> None:
        MaybeState.modify_f((lambda s: Just(s + ' updated'))).run_s('state').should.equal(Just('state updated'))

    def flat_map_f(self) -> None:
        l = Left('boing')
        EitherState.pure(1).flat_map_f(lambda a: l).run('start').should.equal(l)

    def zip(self) -> None:
        EvalState.pure(1).zip(EvalState.pure(2)).run_a(None)._value().should.equal(List(1, 2))

    def eff(self) -> None:
        def f(a: int) -> EvalState[int, Either[str, int]]:
            return EvalState.pure(Right(2))
        s0 = EvalState.pure(Right(1))
        s0.eff(Either).flat_map(f).value.run(1)._value().should.equal((1, Right(2)))
        (s0 // EvalState.modify(I).replace).eff(Either).flat_map(f).value.run(1)._value().should.equal((1, Right(2)))

    def id(self) -> None:
        s = IdState.inspect(lambda s0: s0 * 2).flat_map(lambda a: IdState.pure(a + 4))
        s.run(5).should.equal(Id((5, 14)))

    def transform_s(self) -> None:
        def trans_from(r: str) -> int:
            return int(r)
        def trans_to(r: str, s: int) -> str:
            return str(s)
        s1 = State(Id(lambda s: Id((s + 1, None)))).transform_s(trans_from, trans_to)
        s1.run_s('2').value.should.equal('3')

    def transform_f(self) -> None:
        MaybeState.pure(7).transform_f(EitherState, lambda m: m.to_either('none')).run_a(None).should.equal(Right(7))

    def lift_left(self) -> None:
        EitherState.lift(Left(1)).run_a(None).should.equal(Left(1))

__all__ = ('StateSpec',)
