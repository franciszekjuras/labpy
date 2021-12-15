# About

**labpython** (imported as `labpy`) is a collection of modules created to simplify gathering and processing experimental data. It also features a collection of modules inside `labpy.devices` namespace for high-level communication with various devices using `pyvisa` and `pydaqmx` backends.

# Installation

Package can be installed from PyPI using:
```
pip install labpython
```
By default dependencies for communication with devices are not installed. Use `[devices]` argument to change that behavior:
```
pip install labpython[devices]
```
To install directly from github use (with optional `#[devices]`):
```
pip install https://github.com/franciszekjuras/labpy/tarball/master#[devices]
```
If you want to modify the package source code it's convenient to install it in developer mode. In order to do this:
- create and activate a [virtual environment](https://docs.python.org/3/library/venv.html),
- clone or download repo from github,
- navigate to its main directory (the one in which this `README.md` resides),
- execute: `pip install -e .[devices]`
- now you can use `import labpy` freely and any changes to source code will be visible without reinstallation