from amino.util.coconut_mypy import process_output
from amino import List, Map
from amino.test.spec_spec import Spec


class CoconutMypySpec(Spec):

    def substitute_lnums(self) -> None:
        lines = List(
            'sooo...In module imported from: asdf',
            'amino/maybe.py:116:5: error: broken',
            'foo/bar/__coconut__.py:22: error: nutt'
        )
        return
        process_output(lines).should.equal(List(Map(lnum=82, text='broken', valid=1, maker_name='mypy', col=5)))

__all__ = ('CoconutMypySpec')
