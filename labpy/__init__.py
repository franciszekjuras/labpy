import os
dirname = os.path.dirname(__file__)
try:
    with open(os.path.join(dirname, '../README.md')) as f:
        __doc__ = f.read()
except:
    pass
import importlib.metadata
__version__ = importlib.metadata.version('labpython')
