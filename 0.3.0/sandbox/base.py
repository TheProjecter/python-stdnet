import os
import sys

try:
    import stdnet
except:
    stdnet_dir = os.path.split(os.path.split(os.path.abspath(os.path.dirname(__file__)))[0])[0]
    sys.path.append(stdnet_dir)
    import stdnet