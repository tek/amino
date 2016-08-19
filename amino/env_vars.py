import os

from amino.map import Map


class EnvVars(object):

    @property
    def vars(self):
        return Map(os.environ)

    def __contains__(self, name):
        return name in self.vars

    def __getitem__(self, name):
        return self.vars.get(name)

    def __setitem__(self, name, value):
        self.vars[name] = value

env = EnvVars()

__all__ = ('EnvVars', 'env')
