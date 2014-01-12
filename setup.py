from setuptools import setup
from flosculus import _meta

with open("README.rst") as f:
    long_desc = f.read()


setup(
    name="flosculus",
    version=_meta.__version__,
    description="Tail your log, extract the data, and send it to Fluentd",
    long_description=long_desc,
    author="Isman Firmansyah",
    author_email="isman.firmansyah@gmail.com",
    url="https://github.com/iromli/flosculus",
    packages=["flosculus"],
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
    ],
    entry_points={
        "console_scripts": ["flosculusd=flosculus.cli:main"],
    },
    zip_safe=False,
    install_requires=[
        "logbook>=0.6.0",
        "configparser>=3.3.0r2",
        "docopt>=0.6.1",
        "fluent-logger>=0.3.3",
    ],
)
