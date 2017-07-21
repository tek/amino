from amino.state import MaybeState, EitherState, EvalState
from amino.test.spec_spec import Spec
from amino import Just, Left, List, Either, Right, I


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

__all__ = ('StateSpec',)
