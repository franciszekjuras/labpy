import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from labpy.server import Server

Server().run()
