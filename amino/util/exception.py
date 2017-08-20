from traceback import format_tb

from amino import List, Lists, Maybe


def sanitize_tb(tb: List[str]) -> List[str]:
    return tb.flat_map(lambda a: Lists.wrap(a.splitlines()))


def format_exception(exc: Exception) -> List[str]:
    tb = sanitize_tb(Lists.wrap(format_tb(exc.__traceback__)))
    main = tb.cat(f'{exc.__class__.__name__}: {exc}')
    cause = Maybe(exc.__cause__) / format_exception / (lambda a: a.cons('Cause:')) | List()
    return main + cause

__all__ = ('sanitize_tb', 'format_exception')
