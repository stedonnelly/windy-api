"""
Windy API: Python Windy API package for interacting with the Windy API.
"""

from __future__ import annotations

from .api import WindyAPI

try:
    from windy_api._version import version as __version__
except ImportError:
    # Package not installed or setuptools-scm not run yet
    from importlib.metadata import version

    __version__ = version(__name__)

__all__ = ("__version__", "WindyAPI")
