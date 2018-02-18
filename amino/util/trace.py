import inspect
from types import FrameType
from typing import Any, Tuple

from amino import List, Lists, Path, Either, _, Try, Right, Maybe, L, Nil
from amino.do import do, Do
from amino.func import tailrec


def cframe() -> FrameType:
    return inspect.currentframe()


@do(Either[Exception, Tuple[str, str]])
def frame_data(frame: FrameType) -> Do:
    file = inspect.getsourcefile(frame.f_code)
    path = yield Try(Path, file)
    text = yield Try(path.read_text)
    code = yield Lists.lines(text).lift(frame.f_lineno - 1).to_either('frame_data: invalid line number in frame')
    yield Right((file, code))


def traceback_entry(frame: FrameType, file: str, code: str) -> List[str]:
    line = frame.f_lineno
    fun = frame.f_code.co_name
    clean = code.strip()
    return List(f'  File "{file}", line {line}, in {fun}', f'    {clean}')


@do(Either[str, List[str]])
def frame_traceback_entry(frame: FrameType) -> Do:
    file, code = yield frame_data(frame)
    yield Right(traceback_entry(frame, file, code))


default_internal_packages = List('amino')


def internal_frame(frame: FrameType, pkgs: List[str]=None) -> bool:
    pkg = frame.f_globals.get('__package__')
    return (not isinstance(pkg, str)) or pkg == '' or (pkgs or default_internal_packages).exists(pkg.startswith)


def non_internal_frame(frame: FrameType, pkgs: List[str]=None) -> bool:
    return not internal_frame(frame, pkgs)


def tb_callsite(tb: List[FrameType], pkgs: List[str]=None) -> Either[str, FrameType]:
    return tb.find(L(non_internal_frame)(_, pkgs)).to_either('no non-internal frame found')


def frame_callsite(frame: FrameType, pkgs: List[str]=None) -> FrameType:
    @tailrec
    def loop(f: FrameType) -> FrameType:
        return (True, (f.f_back,)) if internal_frame(f, pkgs) else (False, f)
    return loop(frame)


def callsite_traceback_entry(frame: FrameType, pkgs: List[str]=None) -> Do:
    return frame_traceback_entry(frame_callsite(frame, pkgs))


def callsite_info(frame: FrameType, pkgs: List[str]=None) -> List[str]:
    return callsite_traceback_entry(frame, pkgs) | List('  <no callsite info>')


def callsite_source(frame: FrameType, pkgs: List[str]=None) -> str:
    return frame_data(frame_callsite(frame, pkgs)) / _[1] | '<no source>'


__all__ = ('cframe', 'callsite_info', 'callsite_source', 'tb_callsite', 'non_internal_frame', 'internal_frame')
