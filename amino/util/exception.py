import inspect
from typing import Tuple, Callable

from traceback import format_list, format_exception_only, FrameSummary, extract_tb

from amino.data.list import List, Lists
from amino.func import I


def sanitize_tb(tb: List[str]) -> List[str]:
    return tb.flat_map(lambda a: Lists.wrap(a.splitlines())) / (lambda a: a.rstrip())


def format_exception_error(exc: Exception) -> List[str]:
    return sanitize_tb(Lists.wrap(format_exception_only(type(exc), exc)))


def format_one_exception(
        exc: Exception,
        tb_filter: Callable[[List[FrameSummary]], List[FrameSummary]]=I,
        tb_formatter: Callable[[List[str]], List[str]]=I,
        exc_formatter: Callable[[List[str]], List[str]]=I,
) -> Tuple[List[str], List[str]]:
    e_str = exc_formatter(format_exception_error(exc))
    tb = tb_filter(Lists.wrap(extract_tb(exc.__traceback__)))
    tb_str = tb_formatter(sanitize_tb(Lists.wrap(format_list(tb))))
    return e_str, tb_str


def format_cause(exc: Exception, **kw) -> List[str]:
    from amino import Maybe
    return Maybe.optional(exc.__cause__) / (lambda a: format_exception(a, **kw)) / (lambda a: a.cons('Cause:')) | List()


def format_exception(exc: Exception, **kw) -> List[str]:
    e, tb = format_one_exception(exc, **kw)
    main = tb + e
    return main + format_cause(exc, **kw)


def format_stack(stack: List[inspect.FrameInfo]) -> List[str]:
    data = stack.map(lambda a: a[1:-2] + tuple(a[-2] or ['<string>']))
    return sanitize_tb(Lists.wrap(format_list(list(data))))


def format_current_stack() -> List[str]:
    return format_stack(Lists.wrap(inspect.stack()))


__all__ = ('sanitize_tb', 'format_exception', 'format_stack', 'format_current_stack')
