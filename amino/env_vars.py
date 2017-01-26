import os

from amino.map import Map


class EnvVars:

    @property
    def vars(self):
        return Map(os.environ)

    def __contains__(self, name):
        return name in self.vars

    def __getitem__(self, name):
        return self.vars.get(name)

    def __setitem__(self, name, value):
        os.environ[name] = str(value)

env = EnvVars()

__all__ = ('EnvVars', 'env')
