from amino.state import State
from amino.test.spec_spec import Spec
from amino import Maybe, Just, Either, Left


class StateSpec(Spec):

    def pure(self) -> None:
        s = State.pure(1, Maybe)
        s.run('state').should.equal(Just(('state', 1)))

    def flat_map(self) -> None:
        s = State.pure(1, Maybe)
        def f(a: int) -> None:
            return State.inspect(lambda s: len(s) + a, Maybe)
        s1 = s.flat_map(f)
        return s1.run('str').should.equal(Just(('str', 4)))

    def modify(self) -> None:
        State.modify((lambda s: s + ' updated'), Maybe).run_s('state').should.equal(Just('state updated'))

    def flat_map_f(self) -> None:
        l = Left('boing')
        State.pure(1, Either).flat_map_f(lambda a: l).run('start').should.equal(l)

__all__ = ('StateSpec',)
