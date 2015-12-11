import logging
import sys
from pathlib import Path  # type: ignore

from tryp.lazy import lazy  # type: ignore

import tryp

VERBOSE = 15
DDEBUG = 5
logging.addLevelName(VERBOSE, 'VERBOSE')
logging.addLevelName(DDEBUG, 'DDEBUG')


def verbose(self, message, *args, **kws):
    if self.isEnabledFor(VERBOSE):
        self._log(VERBOSE, message, args, **kws)


def ddebug(self, message, *args, **kws):
    if self.isEnabledFor(DDEBUG):
        self._log(DDEBUG, message, args, **kws)

logging.Logger.verbose = verbose  # type: ignore
logging.Logger.ddebug = ddebug  # type: ignore

log = tryp_root_logger = logging.getLogger('tryp')


def tryp_logger(name: str):
    return tryp_root_logger.getChild(name)

_stdout_logging_initialized = False


def init_loglevel(logger: logging.Logger, level: int=None):
    if level is not None:
        logger.setLevel(level)
    elif tryp.development:
        logger.setLevel(VERBOSE)


def tryp_stdout_logging(level: int=None):
    global _stdout_logging_initialized
    if not _stdout_logging_initialized:
        tryp_root_logger.addHandler(logging.StreamHandler(stream=sys.stdout))
        init_loglevel(tryp_root_logger, level)
        _stdout_logging_initialized = True


logfile = Path.home() / '.python' / 'log'  # type: ignore
_file_logging_initialized = False


def tryp_file_logging(level: int=None):
    global _file_logging_initialized
    if not _file_logging_initialized:
        logfile.parent.mkdir(exist_ok=True)
        tryp_root_logger.addHandler(logging.FileHandler(str(logfile)))
        init_loglevel(tryp_root_logger, level)
        _file_logging_initialized = True


class Logging(object):

    @property
    def log(self) -> logging.Logger:
        return self._log

    @lazy
    def _log(self) -> logging.Logger:
        return tryp_logger(self.__class__.__name__)

__all__ = ['tryp_root_logger', 'tryp_stdout_logging', 'tryp_file_logging']
