# PyFaceB
__author__ = 'Kevin Stanton (kevin@sproutsocial.com)'
__version__ = '0.1.6'

from .api import *
from .exceptions import FBException

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

# ... Clean up.
del logging
del NullHandler
