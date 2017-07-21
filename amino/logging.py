import re
import logging
from logging import LogRecord
import operator
from typing import Callable, Any
import sys
from pathlib import Path

from amino.lazy import lazy

import amino

VERBOSE = 15
DDEBUG = 5
logging.addLevelName(VERBOSE, 'VERBOSE')
logging.addLevelName(DDEBUG, 'DDEBUG')


class LazyRecord(logging.LogRecord):

    def __init__(self, name, level, pathname, lineno, msg, args, exc_info, func=None, sinfo=None,  # type: ignore
                 **kwargs) -> None:
        super().__init__(name, level, pathname, lineno, msg, args, exc_info, func=func, sinfo=sinfo)
        self._data = msg
        self._args = args

    @lazy
    def _cons_message(self) -> str:
        return (
            self._data(*self._args)
            if callable(self._data) else self._data.join_lines
            if isinstance(self._data, amino.List) else
            str(self._data)
        )

    def getMessage(self) -> str:
        return self._cons_message if self.levelname == 'DDEBUG' else super().getMessage()


class Logger(logging.Logger):

    def verbose(self, message, *args, **kws):
        if self.isEnabledFor(VERBOSE):
            self._log(VERBOSE, message, args, **kws)

    def ddebug(self, f: Callable[..., str], *args: Any) -> None:
        if self.isEnabledFor(DDEBUG):
            self._log(DDEBUG, f, args)  # type: ignore

    def caught_exception(self, when: str, exc: Exception, *a: Any, **kw: Any) -> None:
        headline = 'caught exception while {}:'.format(when)
        self.exception(headline, exc_info=(type(exc), exc, exc.__traceback__))

    def makeRecord(self, name: str, level: int, fn: str, lno: int, msg: Any, args: Any, exc_info: Any, func: Any=None,
                   extra: Any=None, sinfo: Any=None) -> LogRecord:
        return LazyRecord(name, level, fn, lno, msg, args, exc_info, func, sinfo)


# logging.Logger.verbose = Logger.verbose  # type: ignore
# logging.Logger.ddebug = Logger.ddebug  # type: ignore
# logging.Logger.caught_exception = Logger.caught_exception  # type: ignore

log = amino_root_logger = logging.getLogger('amino')
log.setLevel(DDEBUG)


def install_logger_class() -> None:
    logging.setLoggerClass(Logger)

install_logger_class()


def amino_logger(name: str) -> logging.Logger:
    return amino_root_logger.getChild(name)

_stdout_logging_initialized = False

_level_env_var = 'AMINO_LOG_LEVEL'


def env_log_level() -> int:
    return amino.env[_level_env_var]


def init_loglevel(handler: logging.Handler, level: int=None) -> None:
    (
        amino.Maybe.check(level)
        .o(env_log_level)
        .o(amino.Boolean(amino.development).flat_m(VERBOSE)) %
        handler.setLevel
    )

amino_stdout_handler = logging.StreamHandler(stream=sys.stdout)


def amino_stdout_logging(level: int=None) -> None:
    global _stdout_logging_initialized
    if not _stdout_logging_initialized:
        amino_root_logger.addHandler(amino_stdout_handler)
        init_loglevel(amino_stdout_handler, level)
        _stdout_logging_initialized = True


default_logfile = Path.home() / '.python' / 'log'
_file_fmt = ('{asctime} [{levelname} @ {name}:{funcName}:{lineno}] {message}')


def amino_file_logging(logger: logging.Logger, level: int=logging.DEBUG,
                       logfile: Path=default_logfile, fmt: str=None) -> None:
    logfile.parent.mkdir(exist_ok=True)
    formatter = logging.Formatter(fmt or _file_fmt, style='{')
    handler = logging.FileHandler(str(logfile))
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    init_loglevel(handler, level)


def amino_root_file_logging(level: int=logging.DEBUG, **kw: Any) -> None:
    amino_file_logging(amino_root_logger, level, **kw)


class Logging:

    @property
    def log(self) -> Logger:
        return self._log

    @lazy
    def _log(self) -> Logger:
        return amino_logger(self.__class__.__name__)

    def _p(self, a):
        v = self.log.verbose
        v(a)
        return a

    def _dbg(self, fmt, level=DDEBUG):
        def log(a):
            msg = fmt.format(a)
            self.log.log(level, msg)
            return a
        return log


def sub_loggers(loggers, root):
    from amino import Map, _, L
    children = loggers.keyfilter(L(re.match)('{}\.[^.]+$'.format(root), _))
    sub = (children.k / L(sub_loggers)(loggers, _))\
        .fold_left(Map())(operator.pow)
    return Map({loggers[root]: sub})


def logger_tree(root):
    from amino import __, Map
    m = Map(logging.Logger.manager.loggerDict)
    all = m.keyfilter(__.startswith(root))
    return sub_loggers(all, 'amino')


def indent(strings, level, width=1):
    ws = ' ' * level * width
    return strings.map(ws.__add__)


def format_logger_tree(tree, fmt_logger, level=0):
    from amino import _, L
    sub_f = L(format_logger_tree)(_, fmt_logger, level=level + 1)
    formatted = tree.bimap(fmt_logger, sub_f)
    return '\n'.join(indent(formatted.map2('{}\n{}'.format), level))


def print_info(out: Callable[[str], None]):
    lname = lambda l: logging.getLevelName(l.getEffectiveLevel())
    hlname = lambda h: logging.getLevelName(h.level)
    def handler(h):
        return '{}({})'.format(h.__class__.__name__, hlname(h))
    def logger(l):
        handlers = ','.join(list(map(handler, l.handlers)))
        return '{}: {} {}'.format(l.name, lname(l), handlers)
    out(format_logger_tree(logger_tree('amino'), logger))

__all__ = ('amino_root_logger', 'amino_stdout_logging', 'amino_file_logging',
           'amino_root_file_logging')
