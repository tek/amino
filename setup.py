from setuptools import setup, find_packages

version_parts = (7, 9, 0)
version = '.'.join(map(str, version_parts))

gh_lenses =\
    'git+https://github.com/ingolemo/python-lenses.git#egg=lenses'

setup(
    name='tryp',
    description='fp data structures',
    version=version,
    author='Torsten Schmits',
    author_email='torstenschmits@gmail.com',
    license='MIT',
    url='https://github.com/tek/tryp',
    packages=find_packages(exclude=['unit', 'unit.*']),
    install_requires=[
        'fn',
        'toolz',
        'lenses',
    ],
    tests_require=[
        'spec',
        'flexmock',
        'sure',
    ],
    dependency_links=[
        gh_lenses,
    ]
)
