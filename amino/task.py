import traceback
import inspect
from typing import Callable, TypeVar, Generic, Any

from amino import Either, Right, Left, Maybe, List, Empty, __, Just, env, _
from amino.tc.base import Implicits, ImplicitsMeta
from amino.anon import format_funcall
from amino.logging import log

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
        def remove_internal():
            start = rev.index_where(_.function == 'unsafe_perform_sync')
            return start / remove_recursion | rev
        def find_loc():
            return (self.stack
                    .find(lambda a: '/amino/' not in a.filename)
                    .to_list)
        frames = find_loc() if Task.stack_only_location else remove_internal()
        data = frames / (lambda a: a[1:-2] + tuple(a[-2]))
        return ''.join(traceback.format_list(list(data)))

    def __str__(self):
        from traceback import format_tb
        msg = 'Task exception{}\nCause:\n{}{}: {}\n\nCallback:\n{}'
        ex = ''.join(format_tb(self.cause.__traceback__))
        loc = ('' if self.stack.empty else
               ' at:\n{}'.format(self.format_stack))
        return msg.format(loc, ex, self.cause.__class__.__name__, self.cause,
                          self.f)


class TaskMeta(ImplicitsMeta):

    @property
    def zero(self):
        return Task.now(None)


class TaskCallback:

    @staticmethod
    def _get_stack():
        return inspect.stack()

    def __init__(self, f: Callable, as_string=Empty()) -> None:
        self.f = f
        self.stack = TaskCallback._get_stack() if Task.record_stack else []
        # if `f` is not wrapped in lambda, get_or_else will call it
        self.as_string = str(as_string | (lambda: f))

    def run(self):
        try:
            return self.f()
        except TaskException as e:
            raise e
        except Exception as e:
            raise TaskException(self.as_string, self.stack, e)


class Task(Generic[A], Implicits, implicits=True, metaclass=TaskMeta):
    record_stack = 'AMINO_RECORD_STACK' in env
    stack_only_location = True

    @staticmethod
    def call(f: Callable[..., A], *a, **kw):
        try:
            s = format_funcall(f, a, kw)
        except Exception as e:
            s = str(f)
            log.error(e)
        return Task(lambda: f(*a, **kw), as_string=Just(s))

    @staticmethod
    def now(a: A) -> 'Task[A]':
        return Task(lambda: a, as_string=Just(repr(a)))

    @staticmethod
    def just(a: A) -> 'Task[Maybe[A]]':
        return Task.now(Just(a))

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

    def __init__(self, f: Callable[[], A], as_string=Empty()) -> None:
        self._callback = TaskCallback(f, as_string)

    def run(self):
        return self._callback.run()

    def __repr__(self):
        return 'Task({})'.format(self._callback.as_string)

    def attempt(self) -> Either[Exception, A]:
        try:
            return Right(self.run())
        except TaskException as e:
            return Left(e)

    unsafe_perform_sync = attempt

    def and_then(self, nxt: 'Task[B]'):
        return self.flat_map(lambda a: nxt)

    __add__ = and_then

    @property
    def as_string(self):
        return self._callback.as_string

    def join_maybe(self, err):
        return self.flat_map(lambda a: Task.from_maybe(a, err))

    @property
    def join_either(self):
        return self.flat_map(Task.from_either)


def Try(f: Callable[..., A], *a, **kw) -> Either[Exception, A]:
    return Task.call(f, *a, **kw).attempt()


def task(fun):
    def dec(*a, **kw):
        return Task.call(fun, *a, **kw)
    return dec

__all__ = ('Task', 'Try', 'task')
