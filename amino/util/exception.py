from traceback import format_tb

from amino import List, Lists


def sanitize_tb(tb: List[str]) -> List[str]:
    return tb.flat_map(lambda a: Lists.wrap(a.splitlines()))


def format_exception(exc: Exception) -> List[str]:
    tb = sanitize_tb(Lists.wrap(format_tb(exc.__traceback__)))
    return tb.cat(f'{exc.__class__.__name__}: {exc}')

__all__ = ('sanitize_tb', 'format_exception')
