import os
import importlib.metadata
__version__ = importlib.metadata.version('labpython')
dirname = os.path.dirname(__file__)
__doc__ = f"`labpython == {__version__}`\n"
try:
    with open(os.path.join(dirname, '../README.md')) as f:
        __doc__ += f.read()
except:
    pass
