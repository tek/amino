import time
import inspect
from contextlib import contextmanager
from typing import Iterator, cast
from types import FrameType

from amino.logging import module_log

log = module_log()


@contextmanager
def timed() -> Iterator[None]:
    mod = inspect.currentframe()
    caller = cast(FrameType, mod).f_back.f_back
    name = caller.f_globals['__name__']
    start = time.time()
    yield
    total = time.time() - start
    log.info(f'>> {name}: {total}')


__all__ = ('timed',)
