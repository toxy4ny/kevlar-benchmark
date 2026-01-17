"""Deprecated: Use 'from kevlar.agents import RealLangChainAgent' instead."""

import warnings

warnings.warn(
    "Importing from real_agent_adapter is deprecated. "
    "Use 'from kevlar.agents import RealLangChainAgent' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from kevlar.agents.langchain import RealLangChainAgent

__all__ = ["RealLangChainAgent"]
