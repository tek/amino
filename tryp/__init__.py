import pathlib
from fn import _  # type: ignore

from tryp.maybe import Maybe, Just, Empty, may, flat_may  # type: ignore
from tryp.list import List  # type: ignore
from tryp.lazy_list import LazyList  # type: ignore
from tryp.map import Map  # type: ignore
from tryp.either import Left, Right, Either  # type: ignore
from tryp.future import Future
from tryp.boolean import Boolean  # type: ignore
from tryp.func import curried, F  # type: ignore
from tryp.anon import __
from tryp.env_vars import env
from tryp.task import Try

development = 'TRYP_DEVELOPMENT' in env
integration_test = 'TRYP_INTEGRATION' in env

Path = pathlib.Path

__all__ = ('Maybe', 'Just', 'Empty', 'may', 'List', 'Map', '_', 'Future',
           'Boolean', 'development', 'flat_may', 'curried', '__', 'F', 'Left',
           'Right', 'Either', 'env', 'Try', 'LazyList')
