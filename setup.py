from pathlib import Path

from setuptools import setup, find_packages

print(Path.cwd())
print(list(Path.cwd().iterdir()))

exec(Path('version.py').read_text())

setup(
    name='tryp',
    description='tryp tools',
    version=version,  # NOQA
    author='Torsten Schmits',
    author_email='torstenschmits@gmail.com',
    license='MIT',
    url='https://github.com/tek/tryp',
    packages=find_packages(exclude=['unit', 'unit.*']),
    install_requires=[
        'fn',
        'toolz',
    ]
)
