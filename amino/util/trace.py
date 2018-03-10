import inspect
from types import FrameType
from typing import Any, Tuple

from amino import List, Lists, Path, Either, _, Try, Right, Maybe, L, Nil
from amino.do import do, Do
from amino.func import tailrec


def cframe() -> FrameType:
    return inspect.currentframe()


@do(Either[Exception, str])
def file_line(file: str, lineno: int) -> Do:
    path = yield Try(Path, file)
    text = yield Try(path.read_text)
    yield Lists.lines(text).lift(lineno).to_either('frame_data: invalid line number in frame')


def frame_data(frame: FrameType) -> Tuple[str, str]:
    file = inspect.getsourcefile(frame.f_code)
    code = file_line(file, frame.f_lineno - 1).value_or(lambda err: f'invalid file entry `{file}`: {err}')
    return file, code


def traceback_entry(frame: FrameType, file: str, code: str) -> List[str]:
    line = frame.f_lineno
    fun = frame.f_code.co_name
    clean = code.strip()
    return List(f'  File "{file}", line {line}, in {fun}', f'    {clean}')


def frame_traceback_entry(frame: FrameType) -> List[str]:
    file, code = frame_data(frame)
    return traceback_entry(frame, file, code)


default_internal_packages = List('amino')


def internal_frame(frame: FrameType, pkgs: List[str]=None) -> bool:
    pkg = frame.f_globals.get('__package__')
    name = frame.f_code.co_filename or ''
    return (
        (not isinstance(pkg, str)) or
        pkg == '' or
        (pkgs or default_internal_packages).exists(pkg.startswith) or
        not name.endswith('.py')
    )


def non_internal_frame(frame: FrameType, pkgs: List[str]=None) -> bool:
    return not internal_frame(frame, pkgs)


def tb_callsite(tb: List[FrameType], pkgs: List[str]=None) -> Either[str, FrameType]:
    return tb.find(L(non_internal_frame)(_, pkgs)).to_either('no non-internal frame found')


def frame_callsite(frame: FrameType, pkgs: List[str]=None) -> FrameType:
    @tailrec
    def loop(f: FrameType) -> FrameType:
        return (True, (f.f_back,)) if not (f is None or f.f_back is None) and internal_frame(f, pkgs) else (False, f)
    return loop(frame)


def callsite_traceback_entry(frame: FrameType, pkgs: List[str]=None) -> List[str]:
    return frame_traceback_entry(frame_callsite(frame, pkgs))


def callsite_info(frame: FrameType, pkgs: List[str]=None) -> List[str]:
    return Maybe.optional(frame) / L(callsite_traceback_entry)(_, pkgs) | List('  <no callsite info>')


def callsite_source(frame: FrameType, pkgs: List[str]=None) -> str:
    return Maybe.optional(frame) / (lambda f: frame_data(frame_callsite(f, pkgs))) / _[1] | '<no source>'


__all__ = ('cframe', 'callsite_info', 'callsite_source', 'tb_callsite', 'non_internal_frame', 'internal_frame')
