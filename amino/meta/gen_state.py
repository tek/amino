from typing import Any

from amino import Path, List, IO, do, Do, Nil
from amino.meta.gen import codegen, CodegenTask, codegen_write

here = Path(__file__).absolute().parent
template_path = here.parent.parent / 'templates' / 'state.py'


def state_task(
        tpe: str,
        path: str,
        tvar: List[str]=Nil,
        class_extra: str='',
        meta_extra: str='',
        ctor_extra: str='',
        extra_import: List[str]=Nil,
        extra: str='',
) -> CodegenTask:
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
        ('{class_extra}', class_extra),
        ('{meta_extra}', meta_extra),
        ('{ctor_extra}', ctor_extra),
        ('{extra_import}', extra_import.join_lines),
        ('{extra}', extra),
        ('StateBase', 'StateT'),
    )
    return CodegenTask(template_path, subs, Nil)


def generate_state(write: bool, name: str, *a: Any, **kw: Any) -> IO[str]:
    task = state_task(*a, **kw)
    outpath = here.parent / 'state' / f'{name}.py'
    return codegen_write(task, outpath) if write else codegen(task)


@do(IO[None])
def generate_states() -> Do:
    yield generate_state(True, 'maybe', 'Maybe', 'amino.maybe')
    yield generate_state(True, 'eval', 'Eval', 'amino.eval')
    yield generate_state(True, 'io', 'IO', 'amino.io')
    yield generate_state(True, 'id', 'Id', 'amino.id')
    yield generate_state(True, 'either', 'Either', 'amino.either', tvar=List('E'))


__all__ = ('generate_state', 'generate_states',)
