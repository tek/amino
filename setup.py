from setuptools import setup, find_packages

version_parts = (7, 3, 0)
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
    ],
    tests_require=[
        'spec',
        'flexmock',
        'sure',
    ],
)
