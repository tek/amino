from typing import Any

from amino import Path, List, IO, do, Do, Nil
from amino.meta.gen import codegen, CodegenTask, codegen_write

here = Path(__file__).parent


def state_task(name: str, tpe: str, path: str, tvar: List[str]=Nil) -> CodegenTask:
    tpar = tvar.map(lambda a: f'{a}, ').mk_string('')
    tvars = tvar.map(lambda a: f'{a} = TypeVar(\'{a}\')').join_lines
    tpe_import = f'from {path} import {tpe}'
    subs = List(
        (r'\bF\[', f'{tpe}[{tpar}'),
        (r'\bF\b', tpe),
        ('StateT\[', f'{tpe}State[{tpar}'),
        ('StateT', f'{tpe}State'),
        ('{tpar}', tpar),
        ('{tvar}', tvars),
        ('{f_import}', tpe_import),
    )
    return CodegenTask('templates/state.py', subs, Nil)


def generate_state(write: bool, name: str, *a: Any, **kw: Any) -> IO[str]:
    task = state_task(name, *a, **kw)
    outpath = here.parent / 'state' / f'{name}.py'
    return codegen_write(task, outpath) if write else codegen(task)


@do(IO[None])
def generate_states() -> Do:
    yield generate_state(True, 'maybe', 'Maybe', 'amino.maybe')
    yield generate_state(True, 'eval', 'Eval', 'amino.eval')
    yield generate_state(True, 'io', 'IO', 'amino.io')
    yield generate_state(True, 'id', 'Id', 'amino.id')
    yield generate_state(True, 'either', 'Either', 'amino.either', tvar=List('E'))


generate_states().fatal
