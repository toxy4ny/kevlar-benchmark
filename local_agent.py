"""Deprecated: Use 'from kevlar.agents import MockCopilotAgent' instead."""

import warnings

warnings.warn(
    "Importing from local_agent is deprecated. "
    "Use 'from kevlar.agents import MockCopilotAgent' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from kevlar.agents.mock import MockCopilotAgent

__all__ = ["MockCopilotAgent"]
