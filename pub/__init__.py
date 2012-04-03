from pub import *

#Right now, I can't import this from setup.py, because pub/pub.py
#imports networkx, which setup.py obviously can't have before
#setup.py installs it. Is there a clean way to solve this problem?
#Until then, just keep updating this version number in setup.py
#and here.
__version__="0.0.2"
