"""Agent adapters for Kevlar benchmark."""

from kevlar.agents.protocol import AgentProtocol
from kevlar.agents.mock import MockCopilotAgent
from kevlar.agents.langchain import RealLangChainAgent, LANGCHAIN_AVAILABLE


def check_langchain_available() -> bool:
    """Check if LangChain dependencies are installed."""
    return LANGCHAIN_AVAILABLE


def check_ollama_available(base_url: str = "http://localhost:11434") -> bool:
    """Check if Ollama is running and accessible."""
    try:
        import urllib.request
        req = urllib.request.Request(f"{base_url}/api/tags", method='GET')
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def check_real_agent_dependencies(base_url: str = "http://localhost:11434") -> dict:
    """Check all dependencies required for real agent mode.

    Returns:
        dict with keys:
            - langchain: bool - LangChain installed
            - ollama: bool - Ollama running
            - available: bool - all deps available
            - missing: list[str] - missing dependencies with install hints
    """
    langchain_ok = check_langchain_available()
    ollama_ok = check_ollama_available(base_url)
    missing = []
    if not langchain_ok:
        missing.append("langchain (pip install langchain langchain-ollama)")
    if not ollama_ok:
        missing.append(f"ollama (not running at {base_url})")
    return {
        'langchain': langchain_ok,
        'ollama': ollama_ok,
        'available': langchain_ok and ollama_ok,
        'missing': missing
    }


__all__ = [
    "AgentProtocol",
    "MockCopilotAgent",
    "RealLangChainAgent",
    "check_langchain_available",
    "check_ollama_available",
    "check_real_agent_dependencies",
]
