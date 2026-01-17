"""Kevlar - Red team security benchmark for AI agents."""

import sys
import warnings

# Suppress pydantic v1 compatibility warning on Python 3.14+
if sys.version_info >= (3, 14):
    warnings.filterwarnings(
        "ignore",
        message="Core Pydantic V1 functionality isn't compatible with Python 3.14",
        category=UserWarning,
        module="langchain_core._api.deprecation"
    )

from kevlar.core.types import SessionLog

__all__ = ["SessionLog"]
__version__ = "1.1.0"
