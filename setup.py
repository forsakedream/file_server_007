from setuptools import setup, find_packages
from os.path import join, dirname

setup(
    name='fileserver007',
    version='1.0.0',
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    install_requires=[r for r in open("requirements.txt", "r") if "#" not in r],
    package_data={
        "": ["*.yaml", "*.ini"]
    },
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'mock', 'pytest-mock', 'pytest-aiohttp', 'pytest-asyncio'],
    entry_points={
        'console_scripts': ['fileserver007=src.main:main']
    }
)
