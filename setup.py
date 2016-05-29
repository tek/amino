from setuptools import setup, find_packages

version_parts = (7, 5, 2)
version = '.'.join(map(str, version_parts))

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
        'lenses',
    ],
    tests_require=[
        'spec',
        'flexmock',
        'sure',
    ],
    dependency_links=[
        'git+https://github.com/ingolemo/python-lenses.git',
    ]
)
