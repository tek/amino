import os
import time
import shutil
import warnings
from datetime import datetime

import spec

import amino
from amino.logging import amino_stdout_logging, Logging
from amino.test.sure_ext import install_assertion_builder, AssBuilder
from amino.test import path


default_timeout = 20 if 'TRAVIS' in os.environ else 5


def later(ass, timeout=default_timeout, intval=0.1):
    start = datetime.now()
    ok = False
    while not ok and (datetime.now() - start).total_seconds() < timeout:
        try:
            ass()
            ok = True
        except AssertionError:
            time.sleep(intval)
    return ass()


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

__all__ = ('Spec', 'IntegrationSpec')
