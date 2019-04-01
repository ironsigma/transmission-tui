"""
Setup script.

To install locally:

    python3 -m pip install .

To install locally with symbolic links:

    python3 -m pip install -e .

To create a source package:

    python3 setup.py sdist

To create a wheel package:

    python3 setup.py bdist_wheel
"""
from setuptools import setup

with open('README.md') as file:
    LONG_DESCRIPTION = file.read()

setup(
    name="transmission-tui",
    description="Transmission terminal user interface",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/ironsigma/transmission-tui",
    version="0.1.0",
    author="Juan D Frias",
    author_email="juandfrias@gmail.com",
    license="MIT",
    packages=["transmission_tui"],
    scripts=['bin/transmission-tui'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console :: Curses",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End User/Desktop",
        "Topic :: Comunications :: File Sharing",
    ],
)
