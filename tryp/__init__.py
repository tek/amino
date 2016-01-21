import os

from fn import _  # type: ignore

from tryp.maybe import Maybe, Just, Empty, may, flat_may  # type: ignore
from tryp.list import List  # type: ignore
from tryp.map import Map  # type: ignore
from tryp.future import Future
from tryp.boolean import Boolean  # type: ignore
from tryp.func import curried
from tryp.anon import __

development = False
integration_test = 'TRYP_INTEGRATION' in os.environ


__all__ = ('Maybe', 'Just', 'Empty', 'may', 'List', 'Map', '_', 'Future',
           'Boolean', 'development', 'flat_may', 'curried', '__')
