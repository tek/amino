import abc
import time
import traceback
import inspect
from typing import Callable, TypeVar, Generic, Any

from fn.recur import tco

from amino import Either, Right, Left, Maybe, List, Empty, __, Just, env, _
from amino.tc.base import Implicits, ImplicitsMeta
from amino.anon import format_funcall, lambda_str, L
from amino.logging import log
from amino.func import F

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


class Task(Generic[A], Implicits, implicits=True, metaclass=TaskMeta):
    debug = 'AMINO_TASK_DEBUG' in env
    stack_only_location = True

    def __init__(self) -> None:
        self.stack = inspect.stack() if Task.debug else []

    @staticmethod
    def suspend(f: Callable[..., A], *a, **kw):
        try:
            s = format_funcall(f, a, kw)
        except Exception as e:
            s = str(f)
            log.error(e)
        return Suspend(F(f, *a, **kw) >> Now, s)

    @staticmethod
    def call(f: Callable[..., A], *a, **kw):
        return Task.suspend(f, *a, **kw)

    @staticmethod
    def now(a: A) -> 'Task[A]':
        return Now(a)

    @staticmethod
    def just(a: A) -> 'Task[Maybe[A]]':
        return Task.now(Just(a))

    @staticmethod
    def failed(err: str) -> 'Task[A]':
        def fail():
            raise Exception(err)
        return Task.suspend(fail)

    @staticmethod
    def from_either(a: Either[Any, A]) -> 'Task[A]':
        return a.cata(Task.failed, Task.now)

    @staticmethod
    def from_maybe(a: Maybe[A], error: str) -> 'Task[A]':
        return a / Task.now | Task.failed(error)

    def run(self):
        @tco
        def run(t):
            if isinstance(t, Now):
                return True, (t.value,)
            elif isinstance(t, Task):
                return True, (t.step,)
            else:
                return False, t
        return run(self)

    @property
    def _name(self):
        return self.__class__.__name__

    def flat_map(self, f: Callable[[A], 'Task[B]'], as_string=Empty()
                 ) -> 'Task[B]':
        s = (as_string |
             (lambda: '{}.flat_map({})'.format(self.as_string, lambda_str(f))))
        return self._flat_map(f, s)

    @abc.abstractmethod
    def _flat_map(self, f: Callable[[A], 'Task[B]'], as_string) -> 'Task[B]':
        ...

    @property
    def step(self):
        try:
            return self._step_timed if Task.debug else self._step
        except TaskException as e:
            raise e
        except Exception as e:
            raise TaskException(self.as_string, self.stack, e)

    @property
    def _step_timed(self):
        start = time.time()
        v = self._step
        dur = time.time() - start
        if dur > 0.1:
            self.log.ddebug('task {} took {:.4f}s'.format(
                self.as_string, dur))
        return v

    @abc.abstractproperty
    def _step(self):
        ...

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

    def join_maybe(self, err):
        return self.flat_map(lambda a: Task.from_maybe(a, err))

    @property
    def join_either(self):
        return self.flat_map(Task.from_either)


class Suspend(Generic[A], Task[A]):

    def __init__(self, thunk: Callable, as_string) -> None:
        super().__init__()
        self.thunk = thunk
        self.as_string = as_string

    @property
    def _step(self):
        return self.thunk()

    def __str__(self):
        return '{}({})'.format(self._name, self.as_string)

    def _flat_map(self, f: Callable[[A], 'Task[B]'], as_string) -> 'Task[B]':
        return BindSuspend(self.thunk, f, as_string)


class BindSuspend(Generic[A], Task[A]):

    def __init__(self, thunk, f: Callable, as_string) -> None:
        super().__init__()
        self.thunk = thunk
        self.f = f
        self.as_string = as_string

    @property
    def _step(self):
        return self.thunk().flat_map(self.f, as_string=Just(self.as_string))

    def __str__(self):
        return '{}({})'.format(self._name, self.as_string)

    def _flat_map(self, f: Callable[[A], 'Task[B]'], as_string) -> 'Task[B]':
        bs = L(BindSuspend)(self.thunk, L(self.f)(_).flat_map(f,
                                                              Just(as_string)),
                            as_string)
        return Suspend(bs, as_string)


class Now(Generic[A], Task[A]):

    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
        self.as_string = str(self)

    @property
    def _step(self):
        return self

    def __str__(self):
        return '{}({})'.format(self._name, self.value)

    def _flat_map(self, f: Callable[[A], 'Task[B]'], as_string) -> 'Task[B]':
        return Suspend(F(f, self.value), as_string)


def Try(f: Callable[..., A], *a, **kw) -> Either[Exception, A]:
    return Task.suspend(f, *a, **kw).attempt()


def task(fun):
    def dec(*a, **kw):
        return Task.suspend(fun, *a, **kw)
    return dec

__all__ = ('Task', 'Try', 'task')
