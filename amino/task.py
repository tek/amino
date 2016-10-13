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

A = TypeVar('A')
B = TypeVar('B')


class TaskException(Exception):
    remove_pkgs = List('amino', 'fn')

    def __init__(self, f, stack, cause) -> None:
        self.f = f
        self.stack = List.wrap(stack)
        self.cause = cause

    @property
    def location(self):
        files = List('task', 'anon', 'instances/task', 'tc/base')
        def filt(entry, name):
            return entry.filename.endswith('/amino/{}.py'.format(name))
        stack = self.stack.filter_not(lambda a: files.exists(L(filt)(a, _)))
        pred = (lambda a: not TaskException.remove_pkgs
                .exists(lambda b: '/{}/'.format(b) in a.filename))
        return stack.find(pred)

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
        frames = (self.location.to_list if Task.stack_only_location else
                  remove_internal())
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
    def delay(f: Callable[..., A], *a, **kw):
        try:
            s = format_funcall(f, a, kw)
        except Exception as e:
            s = str(f)
            log.error(e)
        return Suspend(L(f)(*a, **kw) >> Now, s)

    @staticmethod
    def suspend(f: Callable[..., 'Task[A]'], *a, **kw):
        try:
            s = format_funcall(f, a, kw)
        except Exception as e:
            s = str(f)
            log.error(e)
        return Suspend(L(f)(*a, **kw), s)

    @staticmethod
    def call(f: Callable[..., A], *a, **kw):
        return Task.delay(f, *a, **kw)

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
                return True, (t.step(),)
            else:
                return False, t
        return run(self)

    @property
    def _name(self):
        return self.__class__.__name__

    def flat_map(self, f: Callable[[A], 'Task[B]'], ts=Empty(), fs=Empty()
                 ) -> 'Task[B]':
        ts = ts | (lambda: self.string)
        fs = fs | (lambda: 'flat_map({})'.format(lambda_str(f)))
        return self._flat_map(f, ts, fs)

    @abc.abstractmethod
    def _flat_map(self, f: Callable[[A], 'Task[B]'], ts, fs) -> 'Task[B]':
        ...

    def step(self):
        try:
            return self._step_timed() if Task.debug else self._step()
        except TaskException as e:
            raise e
        except Exception as e:
            raise TaskException(self.string, self.stack, e)

    @abc.abstractmethod
    def _step(self):
        ...

    def _step_timed(self):
        start = time.time()
        v = self._step()
        dur = time.time() - start
        if dur > 0.1:
            self.log.ddebug('task {} took {:.4f}s'.format(self.string, dur))
        return v

    def __repr__(self):
        return 'Task({})'.format(self.string)

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

    def with_string(self, s):
        self.string = s
        return self

    def with_stack(self, s):
        self.stack = s
        return self


class Suspend(Generic[A], Task[A]):

    def __init__(self, thunk: Callable, string) -> None:
        super().__init__()
        self.thunk = thunk
        self.string = string

    def _step(self):
        return self.thunk().with_stack(self.stack)

    def __str__(self):
        return '{}({})'.format(self._name, self.string)

    def _flat_map(self, f: Callable[[A], 'Task[B]'], ts, fs) -> 'Task[B]':
        return BindSuspend(self.thunk, f, ts, fs)


class BindSuspend(Generic[A], Task[A]):

    def __init__(self, thunk, f: Callable, ts, fs) -> None:
        super().__init__()
        self.thunk = thunk
        self.f = f
        self.ts = ts
        self.fs = fs

    def _step(self):
        return (
            self.thunk()
            .flat_map(self.f, fs=Just(self.fs))
            .with_stack(self.stack)
        )

    def __str__(self):
        return '{}({})'.format(self._name, self.string)

    def _flat_map(self, f: Callable[[A], 'Task[B]'], ts, fs) -> 'Task[B]':
        bs = L(BindSuspend)(self.thunk,
                            L(self.f)(_).flat_map(f, Just(ts), Just(fs)), ts,
                            fs)
        return Suspend(bs, '{}.{}'.format(ts, fs))

    @property
    def string(self):
        return '{}.{}'.format(self.ts, self.fs)


class Now(Generic[A], Task[A]):

    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
        self.string = str(self)

    def _step(self):
        return self

    def __str__(self):
        return '{}({})'.format(self._name, self.value)

    def _flat_map(self, f: Callable[[A], 'Task[B]'], ts, fs) -> 'Task[B]':
        return Suspend(L(f)(self.value), '{}.{}'.format(ts, fs))

    @property
    def ts(self):
        return 'Task'

    @property
    def fs(self):
        return 'now({})'.format(self.value)


def Try(f: Callable[..., A], *a, **kw) -> Either[Exception, A]:
    return Task.delay(f, *a, **kw).attempt()


def task(fun):
    def dec(*a, **kw):
        return Task.delay(fun, *a, **kw)
    return dec

__all__ = ('Task', 'Try', 'task')
