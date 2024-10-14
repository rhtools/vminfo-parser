import logging

from ._version import __version__
from .vminfo_parser import main

__all__ = ["main", __version__]

logging.basicConfig()
