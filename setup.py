from setuptools import setup, find_packages

version_parts = (13, 0, 0, 'a', 15)
version = '.'.join(map(str, version_parts))

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
        'toolz',
        'lenses==0.4.0',
    ],
    tests_require=[
        'kallikrein',
    ],
)
