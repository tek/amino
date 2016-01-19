import os

from fn import _  # type: ignore

from tryp.maybe import Maybe, Just, Empty, may, flat_may
from tryp.list import List
from tryp.map import Map
from tryp.future import Future
from tryp.boolean import Boolean
from tryp.func import curried
from tryp.anon import __

development = False
integration_test = 'PROTEOME_INTEGRATION' in os.environ


__all__ = ('Maybe', 'Just', 'Empty', 'may', 'List', 'Map', '_', 'Future',
           'Boolean', 'development', 'flat_may', 'curried', '__')
