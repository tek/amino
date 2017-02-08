import os
import re
import logging
import operator
from typing import Callable, Any
import sys
from pathlib import Path

from amino.lazy import lazy

import amino
from amino.func import call_by_name

VERBOSE = 15
DDEBUG = 5
logging.addLevelName(VERBOSE, 'VERBOSE')
logging.addLevelName(DDEBUG, 'DDEBUG')


class Logger(logging.Logger):

    def verbose(self, message, *args, **kws):
        if self.isEnabledFor(VERBOSE):
            self._log(VERBOSE, message, args, **kws)

    def ddebug(self, message, *args, **kws) -> None:
        if self.isEnabledFor(DDEBUG):
            self._log(DDEBUG, call_by_name(message), args, **kws)

    def caught_exception(self, when, exc, *a, **kw):
        headline = 'caught exception while {}:'.format(when)
        self.exception(headline, exc_info=(type(exc), exc, exc.__traceback__))


logging.Logger.verbose = Logger.verbose  # type: ignore
logging.Logger.ddebug = Logger.ddebug  # type: ignore
logging.Logger.caught_exception = Logger.caught_exception  # type: ignore

log = amino_root_logger = logging.getLogger('amino')
log.setLevel(DDEBUG)


def install_logger_class():
    logging.setLoggerClass(Logger)


def amino_logger(name: str):
    return amino_root_logger.getChild(name)

_stdout_logging_initialized = False

_level_env_var = 'AMINO_LOG_LEVEL'


def init_loglevel(handler: logging.Handler, level: int=None):
    if level is not None:
        handler.setLevel(level)
    elif _level_env_var in os.environ:
        handler.setLevel(os.environ[_level_env_var])
    elif amino.development:
        handler.setLevel(VERBOSE)

amino_stdout_handler = logging.StreamHandler(stream=sys.stdout)


def amino_stdout_logging(level: int=None):
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
