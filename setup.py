from setuptools import setup
from flosculus import _meta


setup(
    name="flosculus",
    version=_meta.__version__,
    description="",
    long_description="",
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
