import os
import re
import logging
from typing import Callable
import sys
from pathlib import Path

from fn import F, _

from amino.lazy import lazy

import amino

VERBOSE = 15
DDEBUG = 5
logging.addLevelName(VERBOSE, 'VERBOSE')
logging.addLevelName(DDEBUG, 'DDEBUG')


class Logger(logging.Logger):

    def verbose(self, message, *args, **kws):
        if self.isEnabledFor(VERBOSE):
            self._log(VERBOSE, message, args, **kws)

    def ddebug(self, message, *args, **kws):
        if self.isEnabledFor(DDEBUG):
            self._log(DDEBUG, message, args, **kws)

    def caught_exception(self, when, exc, *a, **kw):
        headline = 'caught exception while {}:'.format(when)
        self.exception(headline, exc_info=(type(exc), exc, exc.__traceback__))


logging.Logger.verbose = Logger.verbose  # type: ignore
logging.Logger.ddebug = Logger.ddebug  # type: ignore
logging.Logger.caught_exception = Logger.caught_exception  # type: ignore

log = amino_root_logger = logging.getLogger('amino')


def install_logger_class():
    logging.setLoggerClass(Logger)


def amino_logger(name: str):
    return amino_root_logger.getChild(name)

_stdout_logging_initialized = False

_level_env_var = 'AMINO_LOG_LEVEL'


def init_loglevel(logger: logging.Logger, level: int=None):
    if level is not None:
        logger.setLevel(level)
    elif _level_env_var in os.environ:
        logger.setLevel(os.environ[_level_env_var])
    elif amino.development:
        logger.setLevel(VERBOSE)


def amino_stdout_logging(level: int=None):
    global _stdout_logging_initialized
    if not _stdout_logging_initialized:
        amino_root_logger.addHandler(logging.StreamHandler(stream=sys.stdout))
        init_loglevel(amino_root_logger, level)
        _stdout_logging_initialized = True


default_logfile = Path.home() / '.python' / 'log'  # type: ignore
_file_logging_initialized = False


def amino_file_logging(level: int=None, logfile=default_logfile,
                       handler_level: int=logging.INFO):
    global _file_logging_initialized
    if not _file_logging_initialized:
        logfile.parent.mkdir(exist_ok=True)
        handler = logging.FileHandler(str(logfile))
        handler.setLevel(handler_level)
        amino_root_logger.addHandler(handler)
        init_loglevel(amino_root_logger, level)
        _file_logging_initialized = True


class Logging:

    @property
    def log(self) -> Logger:
        return self._log  # type: ignore

    @lazy
    def _log(self) -> Logger:
        return amino_logger(self.__class__.__name__)

    def _p(self, a):
        v = self.log.verbose
        v(a)
        return a


def sub_loggers(loggers, root):
    from amino import Map
    children = loggers.keyfilter(F(re.match, '{}\.[^.]+$'.format(root)))
    sub = (children.k / F(sub_loggers, loggers))\
        .fold_left(Map())(_ ** _)
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
    sub_f = F(format_logger_tree, fmt_logger=fmt_logger, level=level + 1)
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

__all__ = ('amino_root_logger', 'amino_stdout_logging', 'amino_file_logging')
