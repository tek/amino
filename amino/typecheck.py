import os
from typing import List

from typeguard import TypeChecker

tc: TypeChecker = None

_enable_var = 'AMINO_TYPECHECK'
_mods_var = 'AMINO_TYPECHECK_MODS'


def init(mods: List[str]) -> None:
    tc = TypeChecker(mods)
    tc.start()


def boot() -> bool:
    if _enable_var in os.environ:
        mods = os.environ.get(_mods_var) or 'amino'
        init(mods.split(','))
        return True
    else:
        return False

__all__ = ('init', 'boot')
