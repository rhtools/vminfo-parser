import logging

from .__main__ import main
from ._version import __version__

__all__ = [
    "__version__",
    "main",
]

logging.basicConfig()
