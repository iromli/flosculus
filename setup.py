import codecs
import os.path
import re
from setuptools import setup
from setuptools import find_packages


def find_version(*file_paths):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *file_paths), 'r') as f:
        version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open("README.rst") as f:
    long_desc = f.read()


requirements = [
    "logbook",
    "docopt",
    "fluent-logger",
    "six",
]


setup(
    name="flosculus",
    version=find_version("flosculus", "__init__.py"),
    description="Tail your log, extract the data, and send it to Fluentd",
    long_description=long_desc,
    author="Isman Firmansyah",
    author_email="isman.firmansyah@gmail.com",
    url="https://github.com/iromli/flosculus",
    packages=find_packages(),
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
    ],
    entry_points={
        "console_scripts": ["flosculusd=flosculus.cli:main"],
    },
    zip_safe=False,
    install_requires=requirements,
)
