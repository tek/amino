from setuptools import setup, find_packages

version_parts = (9, 5, 7)
version = '.'.join(map(str, version_parts))

gh_lenses =\
    'git+https://github.com/ingolemo/python-lenses.git#egg=lenses'

setup(
    name='amino',
    description='functional data structures and type classes',
    version=version,
    author='Torsten Schmits',
    author_email='torstenschmits@gmail.com',
    license='MIT',
    url='https://github.com/tek/amino',
    packages=find_packages(exclude=['unit', 'unit.*']),
    install_requires=[
        'fn',
        'toolz',
        'lenses',
    ],
    dependency_links=[
        gh_lenses,
    ]
)
