import pathlib

from amino.maybe import Maybe, Just, Empty, may, flat_may
from amino.list import List
from amino.lazy_list import LazyList
from amino.map import Map
from amino.either import Left, Right, Either
from amino.future import Future
from amino.boolean import Boolean
from amino.func import curried, F, I
from amino.anon import __, L, _
from amino.env_vars import env
from amino.task import Try, Task
from amino.logging import Logger, log
from amino.eff import Eff

development = 'AMINO_DEVELOPMENT' in env
integration_test = 'AMINO_INTEGRATION' in env

Path = pathlib.Path

__all__ = ('Maybe', 'Just', 'Empty', 'may', 'List', 'Map', '_', 'Future',
           'Boolean', 'development', 'flat_may', 'curried', '__', 'F', 'Left',
           'Right', 'Either', 'env', 'Try', 'LazyList', 'Logger', 'log', 'I',
           'L', 'Eff', 'Task')
