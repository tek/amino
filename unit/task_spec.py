from tryp.task import Task
from tryp.test import Spec
from tryp import List, Right, __


class TaskSpec(Spec):

    def sequence(self):
        f = lambda: 3
        t = List(Task.now(1), Task.now(2), Task(f)).sequence(Task)
        t.unsafe_perform_sync().should.equal(Right(List(1, 2, 3)))

    def traceback(self):
        class A:
            def rais(self):
                raise Exception('here')
        def fm(a):
            return Task.now(a) / __.rais()
        t = Task.now(A()) // fm
        e = t.unsafe_perform_sync()
        print(e)

    def zip(self):
        t = Task.now(1) & Task.now(2)
        t.unsafe_perform_sync().should.equal(Right((1, 2)))

__all__ = ('TaskSpec',)
