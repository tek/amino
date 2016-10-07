import os
import time
import shutil
import inspect
import warnings
import traceback
from datetime import datetime
from functools import wraps

import spec

import amino
from amino.logging import amino_stdout_logging, Logging
from amino.test.sure_ext import install_assertion_builder, AssBuilder
from amino.test import path
from amino import Path, List


default_timeout = 20 if 'TRAVIS' in os.environ else 3


def later(ass, *a, timeout=default_timeout, intval=0.1, **kw):
    start = datetime.now()
    ok = False
    while not ok and (datetime.now() - start).total_seconds() < timeout:
        try:
            ass(*a, **kw)
            ok = True
        except AssertionError:
            time.sleep(intval)
    return ass(*a, **kw)


class Spec(spec.Spec, Logging):

    def __init__(self):
        self._warnings = True

    def setup(self):
        if path.__base_dir__:
            shutil.rmtree(str(path.temp_path()), ignore_errors=True)
        if self._warnings:
            warnings.resetwarnings()
        amino.development = True
        amino_stdout_logging()
        install_assertion_builder(AssBuilder)

    def teardown(self, *a, **kw):
        warnings.simplefilter('ignore')

    def _wait_for(self, pred, timeout=default_timeout, intval=0.1):
        start = datetime.now()
        while (not pred() and
               (datetime.now() - start).total_seconds() < timeout):
            time.sleep(intval)
        pred().should.be.ok

    def _wait(self, seconds):
        time.sleep(seconds)


class IntegrationSpec(Spec):

    def setup(self):
        os.environ['AMINO_INTEGRATION'] = '1'
        amino.integration_test = True
        super().setup()


def profiled(sort='time'):
    fname = 'prof'
    def dec(f):
        import cProfile
        import pstats
        @wraps(f)
        def wrap(*a, **kw):
            cProfile.runctx('f(*a, **kw)', dict(), dict(f=f, a=a, kw=kw),
                            filename=fname)
            stats = pstats.Stats(fname)
            stats.sort_stats(sort).print_stats(30)
            Path(fname).unlink()
        return wrap
    return dec


def callers(limit=20):
    stack = (List.wrap(inspect.stack())
             .filter_not(lambda a: 'amino' in a.filename))
    data = stack[:limit] / (lambda a: a[1:-2] + tuple(a[-2]))
    return ''.join(traceback.format_list(data))


def timed(f):
    def wrap(*a, **kw):
        import time
        start = time.time()
        v = f(*a, **kw)
        from ribosome.logging import log
        log.info('{}: {}'.format(f.__name__, time.time() - start))
        return v
    return wrap

__all__ = ('Spec', 'IntegrationSpec', 'profiled', 'later', 'timed')
