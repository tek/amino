import numbers

from amino import may


@may
def try_convert_int(data):
    if (
            isinstance(data, numbers.Number) or
            (isinstance(data, str) and data.isdigit())
    ):
        return int(data)

__all__ = ('try_convert_int',)
