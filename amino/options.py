import os

development = 'AMINO_DEVELOPMENT' in os.environ
integration_test = 'AMINO_INTEGRATION' in os.environ

__all__ = ('development', 'integration_test')
