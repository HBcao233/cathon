import importlib.metadata
import gettext
import os

__version__ = importlib.metadata.version('cathon')

cwd = os.path.dirname(os.path.abspath(__file__))
locale_dir = os.path.join(cwd, 'lang')
gettext.install('cat', locale_dir)
