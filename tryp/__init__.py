import pathlib
from fn import _

from tryp.maybe import Maybe, Just, Empty, may, flat_may
from tryp.list import List
from tryp.lazy_list import LazyList
from tryp.map import Map
from tryp.either import Left, Right, Either
from tryp.future import Future
from tryp.boolean import Boolean
from tryp.func import curried, F, I
from tryp.anon import __
from tryp.env_vars import env
from tryp.task import Try
from tryp.logging import Logger, log

development = 'TRYP_DEVELOPMENT' in env
integration_test = 'TRYP_INTEGRATION' in env

Path = pathlib.Path

__all__ = ('Maybe', 'Just', 'Empty', 'may', 'List', 'Map', '_', 'Future',
           'Boolean', 'development', 'flat_may', 'curried', '__', 'F', 'Left',
           'Right', 'Either', 'env', 'Try', 'LazyList', 'Logger', 'log', 'I')
