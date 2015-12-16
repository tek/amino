from setuptools import setup, find_packages  # type: ignore

setup(
    name='tryp',
    description='tryp tools',
    version='2.0.0',
    author='Torsten Schmits',
    author_email='torstenschmits@gmail.com',
    license='MIT',
    url='https://github.com/tek/tryp',
    packages=find_packages(exclude=['unit', 'unit.*']),
    install_requires=[
        'tek',
        'fn',
        'toolz',
    ]
)
