import logging

from .__main__ import main
from ._version import __version__

__all__ = ["main", __version__]

logging.basicConfig()
