import os

from setuptools import setup, find_packages


def open_file(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name))


setup(
    name="error-utils",
    version="0.0.1",
    url="",

    author="Aleksey Reznikov",
    author_email="reznikov@huntflow.ru",

    description="Error-utils: library containing common errors and their handlers for web frameworks",
    long_description=open_file("README.md").read(),

    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    platforms="any",

    install_requires=[],

    extras_require={
        "fastapi": ["fastapi>=0.52.0"],
        "aiohttp": ["aiohttp>=3.0.0"],
        "tornado": ["tornado>=5.1.1"],
    },

    tests_require=[
        "asynctest",
        "pytest",
        "pytest-asyncio",
        "pytest-aiohttp",
        "pytest-tornasync",
        "marshmallow",
        "requests",
    ],

    python_requires=">=3.6"
)
