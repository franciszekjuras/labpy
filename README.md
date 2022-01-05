# About

**labpython** (imported as `labpy`) is a collection of modules created to simplify gathering and processing experimental data. It also features a collection of modules inside `labpy.devices` namespace for high-level communication with various devices using `pyvisa` and `pydaqmx` backends.

# Installation

Package can be installed from PyPI using:
```
pip install labpython
```
Or directly from github:
```
pip install https://github.com/franciszekjuras/labpy/tarball/master
```
Use `[full]` argument to install extra packages for data processing:
```
pip install labpython[full]
```

If you want to modify the package source code it's convenient to install it in developer mode. In order to do this:
- create and activate a [virtual environment](https://docs.python.org/3/library/venv.html),
- clone or download repo from github,
- navigate to its main directory (the one in which this `README.md` resides),
- execute: `pip install -e .`
- now you can use `import labpy` anywhere and any changes to the source code will be visible without reinstallation (if using jupyter kernel must be restarted)

# Documentation

Except some type hints code is undocumented. To get an overview of package structure and existing functions, you can use `pdoc`:
```
pip install pdoc
pdoc labpy
```
