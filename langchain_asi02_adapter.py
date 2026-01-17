"""Deprecated: Use 'from kevlar.agents.adapters import LangChainASI02Agent' instead."""

import warnings

warnings.warn(
    "Importing from langchain_asi02_adapter is deprecated. "
    "Use 'from kevlar.agents.adapters import LangChainASI02Agent' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from kevlar.agents.adapters.asi02 import LangChainASI02Agent

__all__ = ["LangChainASI02Agent"]
