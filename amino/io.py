import abc
import time
import inspect
import typing
import traceback
from pathlib import Path
from threading import Thread
from typing import Callable, TypeVar, Generic, Any, Union, Tuple, Awaitable, Optional

from amino import Either, Right, Left, Maybe, List, __, Just, Lists, L, Nothing, options, _
from amino.eval import Eval
from amino.tc.base import Implicits, ImplicitsMeta
from amino.logging import log
from amino.util.fun import lambda_str, format_funcall
from amino.util.string import ToStr
from amino.do import do, Do
from amino.func import tailrec
from amino.util.trace import callsite_info, frame_callsite, callsite_source, frame_traceback_entry, non_internal_frame
from amino.util.exception import format_exception_error, format_exception
from amino.options import io_debug

A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class IOExceptionBase(Exception, abc.ABC):

    @abc.abstractproperty
    def desc(self) -> str:
        ...

    @abc.abstractproperty
    def internal_packages(self) -> Maybe[List[str]]:
        ...

    def __init__(self, f, stack, cause, frame=None) -> None:
        self.f = f
        self.stack = List.wrap(stack)
        self.cause = cause
        self.frame = frame

    @property
    def lines(self) -> List[str]:
        return self.full_trace_lines if io_debug else self.truncated_trace_lines

    def trace_error(self) -> List[str]:
        return List('<erroneous traceback>')

    @property
    def _internal_packages_arg(self) -> Optional[List[str]]:
        return self.internal_packages | None

    @property
    def full_trace_lines(self) -> List[str]:
        return self.trace_lines_with(format_exception(self.cause))

    @property
    def truncated_trace_lines(self) -> List[str]:
        try:
            tb = Lists.wrap(traceback.walk_tb(self.cause.__traceback__)) / _[0]
            error_loc = (
                tb
                .filter(L(non_internal_frame)(_, self._internal_packages_arg))
                .flat_map(frame_traceback_entry)
            )
            return self.trace_lines_with((error_loc) + format_exception_error(self.cause))
        except Exception as e:
            return self.trace_error()

    def trace_lines_with(self, extra: List[str]) -> List[str]:
        cs = callsite_info(self.frame, self._internal_packages_arg)
        return cs.cons(self.desc) + extra

    def __str__(self) -> str:
        return self.lines.join_lines

    @property
    def callsite(self) -> Any:
        return frame_callsite(self.frame)

    @property
    def callsite_source(self) -> List[str]:
        return callsite_source(self.frame)


class IOException(IOExceptionBase):

    @property
    def desc(self) -> str:
        return 'IO exception'

    @property
    def internal_packages(self) -> Maybe[List[str]]:
        return Nothing


class IOMeta(ImplicitsMeta):

    @property
    def zero(self):
        return IO.now(None)


def safe_fmt(f: Callable[..., Any], a: tuple, kw: dict) -> Eval[str]:
    def s() -> str:
        try:
            return format_funcall(f, Lists.wrap(a), kw)
        except Exception as e:
            return str(f)
            log.error(str(e))
    return Eval.later(s)


class IO(Generic[A], Implicits, ToStr, implicits=True, metaclass=IOMeta):
    debug = options.io_debug.exists
    stack_only_location = True

    @staticmethod
    def delay(f: Callable[..., A], *a: Any, **kw: Any) -> 'IO[A]':
        def g() -> IO[A]:
            return Pure(f(*a, **kw))
        return Suspend(g, safe_fmt(f, a, kw))

    @staticmethod
    def suspend(f: Callable[..., 'IO[A]'], *a: Any, **kw: Any) -> 'IO[A]':
        return Suspend(lambda: f(*a, **kw), safe_fmt(f, a, kw))

    @staticmethod
    def call(f: Callable[..., A], *a, **kw):
        return IO.delay(f, *a, **kw)

    @staticmethod
    def now(a: A) -> 'IO[A]':
        return Pure(a)

    @staticmethod
    def pure(a: A) -> 'IO[A]':
        return Pure(a)

    @staticmethod
    def just(a: A) -> 'IO[Maybe[A]]':
        return IO.now(Just(a))

    @staticmethod
    def failed(err: str) -> 'IO[A]':
        def fail():
            raise Exception(err)
        return IO.suspend(fail)

    @staticmethod
    def from_either(a: Either[Any, A]) -> 'IO[A]':
        return a.cata(IO.failed, IO.now)

    @staticmethod
    def fork_io(f: Callable[..., 'IO[None]'], *a: Any, **kw: Any) -> 'IO[None]':
        def run() -> None:
            try:
                f(*a, **kw).attempt.lmap(lambda a: log.error(f'forked IO failed: {a}'))
            except Exception as e:
                log.caught_exception_error(f'running forked IO', e)
        thread = Thread(target=run)
        return IO.delay(thread.start).replace(thread)

    @staticmethod
    def fork(f: Callable[..., None], *a: Any, **kw: Any) -> 'IO[None]':
        return IO.fork_io(IO.delay, f, *a, **kw)

    @staticmethod
    def from_maybe(a: Maybe[A], error: str) -> 'IO[A]':
        return a / IO.now | IO.failed(error)

    @staticmethod
    def sleep(duration: float) -> 'IO[None]':
        return IO.delay(time.sleep, duration)

    @staticmethod
    def file(path: Path) -> 'IO[List[str]]':
        return IO.delay(path.read_text).map(Lists.lines)

    def __init__(self) -> None:
        self.stack = inspect.stack() if IO.debug else []

    @abc.abstractmethod
    def _flat_map(self, f: Callable[[A], 'IO[B]'], ts: Eval[str], fs: Eval[str]) -> 'IO[B]':
        ...

    @abc.abstractmethod
    def _step(self) -> 'IO[A]':
        ...

    @abc.abstractmethod
    def lambda_str(self) -> Eval[str]:
        ...

    def _arg_desc(self) -> List[str]:
        return List(self.lambda_str()._value())

    def step(self) -> Union[A, 'IO[A]']:
        try:
            return self._step_timed() if IO.debug else self._step()
        except IOException as e:
            raise e
        except Exception as e:
            raise IOException(self.lambda_str()._value(), self.stack, e)

    def run(self) -> A:
        @tailrec
        def run(t: Union[A, 'IO[A]']) -> Union[Tuple[bool, A], Tuple[bool, Tuple[Union[A, 'IO[A]']]]]:
            if isinstance(t, Pure):
                return True, (t.value,)
            elif isinstance(t, IO):
                return True, (t.step(),)
            else:
                return False, t
        return run(self)

    def flat_map(self, f: Callable[[A], 'IO[B]'], ts: Maybe[Eval[str]]=Nothing, fs: Maybe[Eval[str]]=Nothing
                 ) -> 'IO[B]':
        ts1 = ts | self.lambda_str
        fs1 = fs | Eval.later(lambda: f'flat_map({lambda_str(f)})')
        return self._flat_map(f, ts1, fs1)

    def _step_timed(self) -> Union[A, 'IO[A]']:
        start = time.time()
        v = self._step()
        dur = time.time() - start
        if dur > 0.1:
            log.debug2(lambda: 'IO {} took {:.4f}s'.format(self.string(), dur))
        return v

    def _attempt(self) -> Either[IOException, A]:
        try:
            return Right(self.run())
        except IOException as e:
            return Left(e)

    def attempt_run(self) -> Either[IOException, A]:
        return self._attempt()

    @property
    def attempt(self) -> Either[IOException, A]:
        return self._attempt()

    @property
    def fatal(self) -> A:
        return self.attempt.get_or_raise()

    def and_then(self, nxt: 'IO[B]') -> 'IO[B]':
        fs = Eval.later(lambda: 'and_then({nxt.lambda_str()})')
        return self.flat_map(lambda a: nxt, fs=Just(fs))

    __add__ = and_then

    def join_maybe(self, err: str) -> 'IO[B]':
        def f(a: Union[A, Maybe[B]]) -> 'IO[B]':
            return (
                IO.from_maybe(a, err)
                if isinstance(a, Maybe) else
                IO.failed(f'`IO.join_maybe` called on {self}')
            )
        return self.flat_map(f, fs=Just(Eval.later('join_maybe({})'.format, err)))

    @property
    def join_either(self) -> 'IO[B]':
        def f(a: Union[A, Either[C, B]]) -> 'IO[B]':
            return (
                IO.from_either(a)
                if isinstance(a, Either) else
                IO.failed(f'`IO.join_either` called on {self}')
            )
        return self.flat_map(f, fs=Just(Eval.now('join_either')))

    def with_stack(self, s: List[inspect.FrameInfo]) -> 'IO[A]':
        self.stack = s
        return self

    def recover(self, f: Callable[[IOException], B]) -> 'IO[B]':
        return IO.delay(lambda: self.attempt).map(__.value_or(f))

    def recover_with(self, f: Callable[[IOException], 'IO[B]']) -> 'IO[B]':
        return IO.delay(lambda: self.attempt).flat_map(__.map(IO.pure).value_or(f))

    def ensure(self, f: Callable[[Either[IOException, A]], 'IO[None]']) -> 'IO[A]':
        return io_ensure(self, f)

    @property
    def coro(self) -> Awaitable[Either[IOException, A]]:
        async def coro() -> Either[IOException, A]:
            return self.attempt
        return coro()


class Suspend(Generic[A], IO[A]):

    def __init__(self, thunk: Callable[[], IO[A]], string: Eval[str]) -> None:
        super().__init__()
        self.thunk = thunk
        self.string = string

    def lambda_str(self) -> Eval[str]:
        return self.string

    def _step(self) -> IO[A]:
        return self.thunk().with_stack(self.stack)

    def _flat_map(self, f: Callable[[A], IO[B]], ts: Eval[str], fs: Eval[str]) -> IO[B]:
        return BindSuspend(self.thunk, f, ts, fs)


class BindSuspend(Generic[A], IO[A]):

    def __init__(self, thunk: Callable[[], IO[A]], f: Callable, ts: Eval[str], fs: Eval[str]) -> None:
        super().__init__()
        self.thunk = thunk
        self.f = f
        self.ts = ts
        self.fs = fs

    def lambda_str(self) -> Eval[str]:
        return (self.ts & self.fs).map2('{}.{}'.format)

    def _step(self) -> IO[A]:
        return (
            self.thunk()
            .flat_map(self.f, fs=Just(self.fs))
            .with_stack(self.stack)
        )

    def _flat_map(self, f: Callable[[A], IO[B]], ts: Eval[str], fs: Eval[str]) -> IO[B]:
        bs = L(BindSuspend)(self.thunk, lambda a: self.f(a).flat_map(f, Just(ts), Just(fs)), ts, fs)
        return Suspend(bs, (ts & fs).map2('{}.{}'.format))


class Pure(Generic[A], IO[A]):

    def __init__(self, value: A) -> None:
        super().__init__()
        self.value = value

    def lambda_str(self) -> Eval[str]:
        return Eval.later(lambda: f'Pure({self.value})')

    def _arg_desc(self) -> List[str]:
        return List(str(self.value))

    def _step(self) -> IO[A]:
        return self

    def _flat_map(self, f: Callable[[A], IO[B]], ts: Eval[str], fs: Eval[str]) -> IO[B]:
        return Suspend(L(f)(self.value), (ts & fs).map2('{}.{}'.format))


def io(fun: Callable[..., A]) -> Callable[..., IO[A]]:
    def dec(*a: Any, **kw: Any) -> IO[A]:
        return IO.delay(fun, *a, **kw)
    return dec


@do(IO[A])
def io_ensure(io: IO[A], f: Callable[[Either[IOException, A]], 'IO[None]']) -> Do:
    result = yield IO.delay(lambda: io.attempt)
    yield f(result)
    yield IO.from_either(result)


__all__ = ('IO', 'io')
