import os


class EnvOption:

    def __init__(self, name: str) -> None:
        self.name = name

    def __bool__(self) -> bool:
        return self.name in os.environ

development = EnvOption('AMINO_DEVELOPMENT')
integration_test = EnvOption('AMINO_INTEGRATION')
anon_debug = EnvOption('AMINO_ANON_DEBUG')

__all__ = ('development', 'integration_test', 'anon_debug')
