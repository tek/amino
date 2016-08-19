from pathlib import Path

__base_dir__ = None


class TestEnvError(Exception):
    pass


def setup(path):
    ''' Use the supplied path to initialise the tests base dir.
    If _path is a file, its dirname is used.
    '''
    if not isinstance(path, Path):
        path = Path(path)
    if not path.is_dir():
        path = path.parent
    global __base_dir__
    __base_dir__ = path


def _check():
    if __base_dir__ is None:
        msg = 'Test base dir not set! Call amino.test.setup(dir).'
        raise TestEnvError(msg)


def temp_path(*components):
    _check()
    return Path(__base_dir__, '_temp', *components)


def temp_dir(*components):
    _dir = temp_path(*components)
    _dir.mkdir(exist_ok=True, parents=True)
    return _dir


def temp_file(*components):
    return temp_dir(*components[:-1]).joinpath(*components[-1:])


def create_temp_file(*components):
    _file = temp_file(*components)
    _file.touch()
    return _file


def fixture_path(*components):
    _check()
    return Path(__base_dir__, '_fixtures', *components)


def load_fixture(*components):
    with fixture_path(*components).open() as f:
        return f.read()


def base_dir():
    return __base_dir__

__all__ = ('create_temp_file', 'temp_file', 'temp_path', 'temp_dir',
           'fixture_path', 'load_fixture', 'base_dir')
