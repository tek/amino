import traceback
import inspect
from typing import Callable, TypeVar, Generic, Any

from amino import Either, Right, Left, Maybe, List, Empty, __, Just
from amino.tc.base import Implicits

A = TypeVar('A')
B = TypeVar('B')


class TaskException(Exception):

    def __init__(self, f, stack, cause) -> None:
        self.f = f
        self.stack = List.wrap(stack)
        self.cause = cause

    @property
    def format_stack(self):
        rev = self.stack.reversed
        def remove_recursion(i):
            pre = rev[:i + 1]
            post = rev[i:].drop_while(__.filename.endswith('/amino/task.py'))
            return pre + post
        start = rev.index_where(lambda a: a.function == 'unsafe_perform_sync')
        stack = start / remove_recursion | rev
        data = stack / (lambda a: a[1:-2] + tuple(a[-2]))
        return ''.join(traceback.format_list(data))

    def __str__(self):
        from traceback import format_tb
        msg = 'Task exception at:\n{}\nCause:\n{}\n{}\n\nCallback:\n{}'
        ex = ''.join(format_tb(self.cause.__traceback__))
        return msg.format(self.format_stack, ex, self.cause, self.f)


class Task(Generic[A], Implicits, implicits=True):

    @staticmethod
    def call(f: Callable[..., A], *a, **kw):
        return Task(lambda: f(*a, **kw))

    @staticmethod
    def now(a: A) -> 'Task[A]':
        return Task(lambda: a, as_string=Just(repr(a)))

    @staticmethod
    def failed(err: str) -> 'Task[A]':
        def fail():
            raise Exception(err)
        return Task(fail)

    @staticmethod
    def from_either(a: Either[Any, A]) -> 'Task[A]':
        return a.cata(Task.failed, Task.now)

    @staticmethod
    def from_maybe(a: Maybe[A], error: str) -> 'Task[A]':
        return a / Task.now | Task.failed(error)

    def __init__(self, f: Callable[[], A], remove: int=1, as_string=Empty()
                 ) -> None:
        self._run = f
        self.stack = inspect.stack()[remove:]
        # if `f` is not wrapped in lambda, get_or_else will call it
        self.as_string = str(as_string | (lambda: f))

    def run(self):
        try:
            return self._run()
        except TaskException as e:
            raise e
        except Exception as e:
            raise TaskException(self.as_string, self.stack, e)

    def __repr__(self):
        return 'Task({})'.format(self.as_string)

    def unsafe_perform_sync(self) -> Either[Exception, A]:
        try:
            return Right(self.run())
        except TaskException as e:
            return Left(e)

    def and_then(self, nxt: 'Task[B]'):
        return self.flat_map(lambda a: nxt)

    __add__ = and_then


def Try(f: Callable[..., A], *a, **kw) -> Either[Exception, A]:
    return Task.call(f, *a, **kw).unsafe_perform_sync()


def task(fun):
    def dec(*a, **kw):
        return Task.call(fun, *a, **kw)
    return dec

__all__ = ('Task', 'Try', 'task')
