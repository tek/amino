from kallikrein import k, Expectation

from amino.util.coconut_mypy import process_output
from amino import List, Map


class CoconutMypySpec:
    '''substitute line numbers in mypy output for coconut files $substitute_lnums
    '''

    def substitute_lnums(self) -> Expectation:
        lines = List(
            'sooo...In module imported from: asdf',
            'amino/maybe.py:116:5: error: broken',
            'foo/bar/__coconut__.py:22: error: nutt'
        )
        return k(process_output(lines)) == List(Map(lnum=82, text='broken', valid=1, maker_name='mypy', col=5))

__all__ = ('CoconutMypySpec')
