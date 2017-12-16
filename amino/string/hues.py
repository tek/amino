'''Stolen from https://github.com/prashnts/hues
'''

from typing import Union, Any, Callable, Type
from collections import namedtuple
from functools import reduce, partial


ANSIColors = namedtuple(
    'ANSIColors',
    [
        'black',
        'red',
        'green',
        'yellow',
        'blue',
        'magenta',
        'cyan',
        'white',
    ]
)

ANSIStyles = namedtuple(
    'ANSIStyles',
    [
        'reset',
        'bold',
        'italic',
        'underline',
        'defaultfg',
        'defaultbg',
    ]
)

# Style Codes
STYLE = ANSIStyles(0, 1, 3, 4, 39, 49)

# Regular Colors
FG = ANSIColors(*range(30, 38))
BG = ANSIColors(*range(40, 48))

# High Intensity Colors
HI_FG = ANSIColors(*range(90, 98))
HI_BG = ANSIColors(*range(100, 108))

# Terminal sequence format
SEQ = '\033[%sm'


def gen_keywords(*args: Union[ANSIColors, ANSIStyles], **kwargs: Union[ANSIColors, ANSIStyles]) -> tuple:
    '''generate single escape sequence mapping.'''
    fields: tuple = tuple()
    values: tuple = tuple()
    for tpl in args:
        fields += tpl._fields
        values += tpl
    for prefix, tpl in kwargs.items():
        fields += tuple(map(lambda x: '_'.join([prefix, x]), tpl._fields))
        values += tpl
    return namedtuple('ANSISequences', fields)(*values)

KEYWORDS = gen_keywords(STYLE, FG, bg=BG, bright=HI_FG, bg_bright=HI_BG)


def zero_break(stack: tuple) -> tuple:
    '''Handle Resets in input stack.
    Breaks the input stack if a Reset operator (zero) is encountered.
    '''
    reducer = lambda x, y: tuple() if y == 0 else x + (y,)
    return reduce(reducer, stack, tuple())


def annihilate(predicate: tuple, stack: tuple) -> tuple:
    '''Squash and reduce the input stack.
    Removes the elements of input that match predicate and only keeps the last
    match at the end of the stack.
    '''
    extra = tuple(filter(lambda x: x not in predicate, stack))
    head = reduce(lambda x, y: y if y in predicate else x, stack, None)
    return extra + (head,) if head else extra


def annihilator(predicate: tuple) -> Callable[[tuple], tuple]:
    '''Build a partial annihilator for given predicate.'''
    return partial(annihilate, predicate)


def dedup(stack: tuple) -> tuple:
    '''Remove duplicates from the stack in first-seen order.'''
    # Initializes with an accumulator and then reduces the stack with first match
    # deduplication.
    reducer = lambda x, y: x if y in x else x + (y,)
    return reduce(reducer, stack, tuple())


def apply(funcs: tuple, stack: tuple) -> tuple:
    '''Apply functions to the stack, passing the resulting stack to next state.'''
    return reduce(lambda x, y: y(x), funcs, stack)


OPTIMIZATION_STEPS = (
    zero_break,               # Handle Resets using `reset`.
    annihilator(FG + HI_FG),  # Squash foreground colors to the last value.
    annihilator(BG + HI_BG),  # Squash background colors to the last value.
    dedup,                    # Remove duplicates in (remaining) style values.
)
optimize = partial(apply, OPTIMIZATION_STEPS)


def colorize(string: str, stack: tuple) -> str:
    '''Apply optimal ANSI escape sequences to the string.'''
    codes = optimize(stack)
    if len(codes):
        prefix = SEQ % ';'.join(map(str, codes))
        suffix = SEQ % STYLE.reset
        return prefix + string + suffix
    else:
        return string


class HueString(str):

    def __new__(cls, string: str, hue_stack: tuple=None) -> Type['HueString']:
        return super(HueString, cls).__new__(cls)

    def __init__(self, string: str, hue_stack: tuple=tuple()) -> None:
        self.__string = string
        self.__hue_stack = hue_stack

    def __getattr__(self, attr: str) -> 'HueString':
        try:
            code = getattr(KEYWORDS, attr)
            hues = self.__hue_stack + (code,)
            return HueString(self.__string, hue_stack=hues)
        except AttributeError as e:
            raise e

    @property
    def colorized(self) -> str:
        return colorize(self.__string, self.__hue_stack)


def huestr(s: str) -> HueString:
    return HueString(s)


def col(a: Any, c: Callable[[HueString], HueString]) -> str:
    return c(huestr(str(a))).colorized


def red(a: Any) -> str:
    return col(a, lambda a: a.red)


def green(a: Any) -> str:
    return col(a, lambda a: a.green)


def yellow(a: Any) -> str:
    return col(a, lambda a: a.yellow)


def blue(a: Any) -> str:
    return col(a, lambda a: a.blue)


def cyan(a: Any) -> str:
    return col(a, lambda a: a.cyan)


def magenta(a: Any) -> str:
    return col(a, lambda a: a.magenta)


__all__ = ('huestr', 'red', 'green', 'yellow', 'blue', 'cyan', 'magenta')
