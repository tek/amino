from types import FunctionType
from typing import Type, Tuple, Any

from amino import List, Map


def type_tail(a: Any) -> str:
    return str(a).split('.')[-1]


def typename(a: Any) -> str:
    return getattr(a, __name__, type_tail(a))


def synth_method(name: str, params: List[Tuple[str, Type]], statements: List[str], _globals: dict) -> FunctionType:
    id = f'synth_{name}__'
    params_s = params.map2(lambda n, t: f'{n}: {typename(t)}').join_comma
    param_globals = Map(params.map2(lambda n, t: (typename(t), t)))
    globs = Map(_globals) ** param_globals
    code = f'''\
def {name}(self, {params_s}) -> None:
{statements.indent(4).join_lines}
globals()['{id}'] = {name}
    '''
    exec(code, globs)
    return globs.pop(id)


def synth_init(params: List[Tuple[str, Type]], _globals: dict) -> FunctionType:
    assign = params.map2(lambda k, v: f'self.{k} = {k}')
    return synth_method('__init__', params, assign, _globals)


__all__ = ('synth_method', 'synth_init')
