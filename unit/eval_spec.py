from amino import eval
from amino.test.spec_spec import Spec
from amino.lazy_list import LazyLists
from amino.eval import Eval


class EvalSpec(Spec):

    def now(self) -> None:
        v = 'amino'
        e = eval.Now(v)
        e.value.should.be(v)

    def always(self) -> None:
        vs = iter(range(2))
        f = lambda: next(vs)
        e = eval.Always(f)
        e.value.should.be(0)
        e.value.should.be(1)

    def later(self) -> None:
        flag = 0
        def f() -> int:
            nonlocal flag
            flag = flag + 1
            return flag
        e = eval.Later(f)
        e.value.should.be(1)
        e.value.should.be(1)

    def map(self) -> None:
        eval.Later(lambda: 5).map(lambda a: a + 4)._value().should.equal(9)

    def flat_map(self) -> None:
        def f(a: int) -> Eval[int]:
            return eval.Now(a * 2)
        e = eval.Now(1)
        e1 = e.flat_map(f)
        e1._value().should.be(2)

    def loop(self) -> None:
        e = (LazyLists.range(1000).fold_left(eval.Now(0))(lambda z, a: z.flat_map(lambda a: eval.Now(a + 1))))
        e._value().should.equal(1000)

__all__ = ('EvalSpec',)
