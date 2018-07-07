from numbers import Number
from typing import Any, Callable

from amino import may, Right, Left, Maybe, Either


@may
def try_convert_int(data: Any) -> Maybe[int]:
    if (
            isinstance(data, Number) or
            (isinstance(data, str) and data.isdigit())
    ):
        return int(data)


def parse_int(i: Any) -> Either[str, int]:
    return Right(i) if isinstance(i, int) else (
        Right(int(i)) if isinstance(i, str) and i.isdigit() else
        Left('could not parse int {}'.format(i))
    )


def add(inc: int) -> Callable[[int], int]:
    def add(z: int) -> int:
        return z + inc
    return add


def sub(inc: int) -> Callable[[int], int]:
    def sub(z: int) -> int:
        return z - inc
    return sub


__all__ = ('try_convert_int', 'parse_int', 'add',)
