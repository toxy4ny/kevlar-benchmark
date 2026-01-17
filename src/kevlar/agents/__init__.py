"""Agent adapters for Kevlar benchmark."""

from kevlar.agents.protocol import AgentProtocol
from kevlar.agents.mock import MockCopilotAgent
from kevlar.agents.langchain import RealLangChainAgent

__all__ = ["AgentProtocol", "MockCopilotAgent", "RealLangChainAgent"]
