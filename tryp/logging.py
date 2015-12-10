import logging
import sys
from pathlib import Path  # type: ignore

from lazy import lazy  # type: ignore

import tryp

log = tryp_root_logger = logging.getLogger('tryp')


def tryp_logger(name: str):
    return tryp_root_logger.getChild(name)


def tryp_stdout_logging():
    tryp_root_logger.addHandler(logging.StreamHandler(stream=sys.stdout))
    if tryp.development:
        tryp_root_logger.setLevel(logging.DEBUG)


logfile = Path.home() / '.python' / 'log'


def tryp_file_logging():
    logfile.parent.mkdir(exist_ok=True)
    tryp_root_logger.addHandler(logging.FileHandler(str(logfile)))


class Logging(object):

    @lazy
    def log(self):
        return tryp_logger(self.__class__.__name__)

__all__ = ['tryp_root_logger', 'tryp_stdout_logging', 'tryp_file_logging']
