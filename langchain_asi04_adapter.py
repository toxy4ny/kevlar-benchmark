"""Deprecated: Use 'from kevlar.agents.adapters import LangChainASI04Agent' instead."""

import warnings

warnings.warn(
    "Importing from langchain_asi04_adapter is deprecated. "
    "Use 'from kevlar.agents.adapters import LangChainASI04Agent' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from kevlar.agents.adapters.asi04 import LangChainASI04Agent

__all__ = ["LangChainASI04Agent"]
