"""Agent adapters for Kevlar benchmark."""

from kevlar.agents.protocol import AgentProtocol
from kevlar.agents.mock import MockCopilotAgent
from kevlar.agents.langchain import RealLangChainAgent, LANGCHAIN_AVAILABLE


def check_langchain_available() -> bool:
    """Check if LangChain dependencies are installed."""
    return LANGCHAIN_AVAILABLE


def check_ollama_available(base_url: str = "http://localhost:11434", model: str = None) -> bool:
    """Check if Ollama is running and accessible.

    Args:
        base_url: Ollama API base URL
        model: Optional model name to check availability (exact match required, e.g. 'llama3.1:8b')
    """
    try:
        import urllib.request
        import json
        req = urllib.request.Request(f"{base_url}/api/tags", method='GET')
        with urllib.request.urlopen(req, timeout=2) as response:
            if response.status != 200:
                return False
            if model:
                data = json.loads(response.read().decode())
                available_models = [m.get('name', '') for m in data.get('models', [])]
                return model in available_models
            return True
    except Exception:
        return False


def check_real_agent_dependencies(
    base_url: str = "http://localhost:11434",
    model: str = None
) -> dict:
    """Check all dependencies required for real agent mode.

    Args:
        base_url: Ollama API base URL
        model: Optional model name to check availability

    Returns:
        dict with keys:
            - langchain: bool - LangChain installed
            - ollama: bool - Ollama running
            - model: bool - Model available (if specified)
            - available: bool - all deps available
            - missing: list[str] - missing dependencies with install hints
    """
    langchain_ok = check_langchain_available()
    ollama_ok = check_ollama_available(base_url)
    model_ok = True
    missing = []

    if not langchain_ok:
        missing.append("langchain (pip install langchain langchain-ollama)")
    if not ollama_ok:
        missing.append(f"ollama (not running at {base_url})")
    elif model:
        model_ok = check_ollama_available(base_url, model)
        if not model_ok:
            missing.append(f"model '{model}' (run: ollama pull {model})")

    return {
        'langchain': langchain_ok,
        'ollama': ollama_ok,
        'model': model_ok,
        'available': langchain_ok and ollama_ok and model_ok,
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
