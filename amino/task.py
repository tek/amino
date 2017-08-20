import abc
import time
import traceback
import inspect
import typing
from typing import Callable, TypeVar, Generic, Any, Union, Tuple, Awaitable

from fn.recur import tco

from amino import Either, Right, Left, Maybe, List, __, Just, env, _, Lists, L, Nothing
from amino.eval import Eval
from amino.tc.base import Implicits, ImplicitsMeta
from amino.logging import log
from amino.util.fun import lambda_str, format_funcall
from amino.util.exception import format_exception, sanitize_tb
from amino.util.string import ToStr

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


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
    def format_stack(self) -> List[str]:
        rev = self.stack.reversed
        def remove_recursion(i):
            pre = rev[:i + 1]
            post = rev[i:].drop_while(__.filename.endswith('/amino/task.py'))
            return pre + post
        def remove_internal():
            start = rev.index_where(_.function == 'unsafe_perform_sync')
            return start / remove_recursion | rev
        frames = (self.location.to_list if Task.stack_only_location else remove_internal())
        data = frames / (lambda a: a[1:-2] + tuple(a[-2]))
        return sanitize_tb(Lists.wrap(traceback.format_list(list(data))))

    @property
    def lines(self) -> List[str]:
        cause = format_exception(self.cause)
        suf1 = '' if self.stack.empty else ' at:'
        tb1 = (List() if self.stack.empty else self.format_stack)
        return tb1.cons(f'Task exception{suf1}').cat('Cause:') + cause + List(
            '',
            'Callback:',
            f'  {self.f}'
        )

    def __str__(self):
        return self.lines.join_lines

IOException = TaskException


class TaskMeta(ImplicitsMeta):

    @property
    def zero(self):
        return Task.now(None)


def safe_fmt(f: Callable[..., Any], a: tuple, kw: dict) -> Eval[str]:
    def s() -> str:
        try:
            return format_funcall(f, Lists.wrap(a), kw)
        except Exception as e:
            return str(f)
            log.error(str(e))
    return Eval.later(s)


class Task(Generic[A], Implicits, ToStr, implicits=True, metaclass=TaskMeta):
    debug = 'AMINO_TASK_DEBUG' in env
    stack_only_location = True

    def __init__(self) -> None:
        self.stack = inspect.stack() if Task.debug else []

    @staticmethod
    def delay(f: Callable[..., A], *a: Any, **kw: Any) -> 'Task[A]':
        return Suspend(L(f)(*a, **kw) >> Now, safe_fmt(f, a, kw))

    @staticmethod
    def suspend(f: Callable[..., 'Task[A]'], *a: Any, **kw: Any) -> 'Task[A]':
        return Suspend(L(f)(*a, **kw), safe_fmt(f, a, kw))

    @staticmethod
    def call(f: Callable[..., A], *a, **kw):
        return Task.delay(f, *a, **kw)

    @staticmethod
    def now(a: A) -> 'Task[A]':
        return Now(a)

    @staticmethod
    def pure(a: A) -> 'IO[A]':
        return Pure(a)

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

    @abc.abstractmethod
    def _flat_map(self, f: Callable[[A], 'Task[B]'], ts: Eval[str], fs: Eval[str]) -> 'Task[B]':
        ...

    @abc.abstractmethod
    def _step(self) -> 'Task[A]':
        ...

    @abc.abstractmethod
    def lambda_str(self) -> Eval[str]:
        ...

    def _arg_desc(self) -> List[str]:
        return List(self.lambda_str()._value())

    def step(self) -> Union[A, 'Task[A]']:
        try:
            return self._step_timed() if Task.debug else self._step()
        except TaskException as e:
            raise e
        except Exception as e:
            raise TaskException(self.lambda_str()._value(), self.stack, e)

    def run(self) -> A:
        @tco
        def run(t: Union[A, 'Task[A]']) -> Union[Tuple[bool, A], Tuple[bool, Tuple[Union[A, 'Task[A]']]]]:
            if isinstance(t, Now):
                return True, (t.value,)
            elif isinstance(t, Task):
                return True, (t.step(),)
            else:
                return False, t
        return run(self)

    def flat_map(self, f: Callable[[A], 'Task[B]'], ts: Maybe[Eval[str]]=Nothing, fs: Maybe[Eval[str]]=Nothing
                 ) -> 'Task[B]':
        ts1 = ts | self.lambda_str
        fs1 = fs | Eval.later(lambda: f'flat_map({lambda_str(f)})')
        return self._flat_map(f, ts1, fs1)

    def _step_timed(self) -> Union[A, 'Task[A]']:
        start = time.time()
        v = self._step()
        dur = time.time() - start
        if dur > 0.1:
            log.debug2(lambda: 'task {} took {:.4f}s'.format(self.string(), dur))
        return v

    def _attempt(self) -> Either[TaskException, A]:
        try:
            return Right(self.run())
        except TaskException as e:
            return Left(e)

    def unsafe_perform_sync(self) -> Either[TaskException, A]:
        return self.attempt

    @property
    def attempt(self) -> Either[TaskException, A]:
        return self._attempt()

    @property
    def fatal(self) -> A:
        return self.attempt.get_or_raise

    def and_then(self, nxt: 'Task[B]') -> 'Task[B]':
        fs = Eval.later(lambda: 'and_then({nxt.lambda_str()})')
        return self.flat_map(lambda a: nxt, fs=Just(fs))

    __add__ = and_then

    def join_maybe(self, err: str) -> 'Task[B]':
        def f(a: Union[A, Maybe[B]]) -> 'Task[B]':
            return (
                Task.from_maybe(a, err)
                if isinstance(a, Maybe) else
                Task.failed(f'`Task.join_maybe` called on {self}')
            )
        return self.flat_map(f, fs=Just(Eval.later('join_maybe({})'.format, err)))

    @property
    def join_either(self) -> 'Task[B]':
        def f(a: Union[A, Either[C, B]]) -> 'Task[B]':
            return (
                Task.from_either(a)
                if isinstance(a, Either) else
                Task.failed(f'`Task.join_either` called on {self}')
            )
        return self.flat_map(f, fs=Just(Eval.now('join_either')))

    def with_stack(self, s: typing.List[inspect.FrameInfo]) -> 'Task[A]':
        self.stack = s
        return self

    def recover(self, f: Callable[[TaskException], B]) -> 'Task[B]':
        return Task.delay(lambda: self.attempt).map(__.value_or(f))

    @property
    def coro(self) -> Awaitable[Either[TaskException, A]]:
        async def coro() -> Either[TaskException, A]:
            return self.attempt
        return coro()


class Suspend(Generic[A], Task[A]):

    def __init__(self, thunk: Callable[[], Task[A]], string: Eval[str]) -> None:
        super().__init__()
        self.thunk = thunk
        self.string = string

    def lambda_str(self) -> Eval[str]:
        return self.string

    def _step(self) -> Task[A]:
        return self.thunk().with_stack(self.stack)

    def _flat_map(self, f: Callable[[A], Task[B]], ts: Eval[str], fs: Eval[str]) -> Task[B]:
        return BindSuspend(self.thunk, f, ts, fs)


class BindSuspend(Generic[A], Task[A]):

    def __init__(self, thunk: Callable[[], Task[A]], f: Callable, ts: Eval[str], fs: Eval[str]) -> None:
        super().__init__()
        self.thunk = thunk
        self.f = f
        self.ts = ts
        self.fs = fs

    def lambda_str(self) -> Eval[str]:
        return (self.ts & self.fs).map2('{}.{}'.format)

    def _step(self) -> Task[A]:
        return (
            self.thunk()
            .flat_map(self.f, fs=Just(self.fs))
            .with_stack(self.stack)
        )

    def _flat_map(self, f: Callable[[A], Task[B]], ts: Eval[str], fs: Eval[str]) -> Task[B]:
        bs = L(BindSuspend)(self.thunk, lambda a: self.f(a).flat_map(f, Just(ts), Just(fs)), ts, fs)
        return Suspend(bs, (ts & fs).map2('{}.{}'.format))


class Now(Generic[A], Task[A]):

    def __init__(self, value: A) -> None:
        super().__init__()
        self.value = value

    def lambda_str(self) -> Eval[str]:
        return Eval.later(lambda: f'Now({self.value})')

    def _arg_desc(self) -> List[str]:
        return List(str(self.value))

    def _step(self) -> Task[A]:
        return self

    def _flat_map(self, f: Callable[[A], Task[B]], ts: Eval[str], fs: Eval[str]) -> Task[B]:
        return Suspend(L(f)(self.value), (ts & fs).map2('{}.{}'.format))

Pure = Now


def Try(f: Callable[..., A], *a: Any, **kw: Any) -> Either[Exception, A]:
    try:
        return Right(f(*a, **kw))
    except Exception as e:
        return Left(e)


def task(fun: Callable[..., A]) -> Callable[..., Task[A]]:
    def dec(*a: Any, **kw: Any) -> Task[A]:
        return Task.delay(fun, *a, **kw)
    return dec

IO = Task

__all__ = ('Task', 'Try', 'task', 'IO')
