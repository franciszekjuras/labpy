import os
dirname = os.path.dirname(__file__)
with open(os.path.join(dirname, '../README.md')) as f:
    __doc__ = f.read()
import importlib.metadata
__version__ = importlib.metadata.version('labpython')
