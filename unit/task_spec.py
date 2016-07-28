from tryp.task import Task
from tryp.test import Spec
from tryp import List, Right


class TaskSpec(Spec):

    def sequence(self):
        f = lambda: 3
        t = List(Task.now(1), Task.now(2), Task(f)).sequence(Task)
        t.unsafe_perform_sync().should.equal(Right(List(1, 2, 3)))

__all__ = ('TaskSpec',)
