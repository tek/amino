import os
from typing import Any

from amino.map import Map
from amino import Either
from amino.io import IO


class EnvVars:

    @property
    def vars(self):
        return Map(os.environ)

    def __contains__(self, name: str) -> bool:
        return self.contains(name)

    def contains(self, name: str) -> bool:
        return name in self.vars

    def __getitem__(self, name: str) -> Either[str, str]:
        return self.get(name)

    def get(self, name: str) -> Either[str, str]:
        return self.vars.lift(name).to_either(f'env var {name} is unset')

    def __setitem__(self, name: str, value: str) -> None:
        self.set(name, value)

    def set(self, name: str, value: str) -> None:
        os.environ[name] = str(value)

    def __delitem__(self, name: str) -> None:
        return self.delete(name)

    def delete(self, name: str) -> None:
        if name in os.environ:
            del os.environ[name]

env = EnvVars()


def set_env(name: str, value: Any) -> IO[None]:
    return IO.delay(env.set, name, str(value))


__all__ = ('EnvVars', 'env')
