from setuptools import setup, find_packages

from tryp.version import version

setup(
    name='tryp',
    description='tryp tools',
    version=version,
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
