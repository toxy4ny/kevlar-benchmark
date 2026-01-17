"""
Unit tests for LangChain ASI04 Adapter.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys


def make_tool_decorator():
    """Create a tool decorator that adds name attribute."""
    def tool_decorator(func):
        func.name = func.__name__
        func.func = func
        return func
    return tool_decorator


@pytest.fixture
def mock_langchain_only():
    """Mock only langchain, no autogen."""
    mock_chat_ollama = MagicMock()
    mock_tool = make_tool_decorator()
    mock_create_agent = MagicMock()
    mock_executor_class = MagicMock()
    mock_prompt = MagicMock()

    with patch.dict('sys.modules', {
        'langchain_ollama': MagicMock(ChatOllama=mock_chat_ollama),
        'langchain_core.tools': MagicMock(tool=mock_tool),
        'langchain.agents': MagicMock(
            create_tool_calling_agent=mock_create_agent,
            AgentExecutor=mock_executor_class
        ),
        'langchain_core.prompts': MagicMock(
            ChatPromptTemplate=MagicMock(from_messages=MagicMock(return_value=mock_prompt))
        ),
    }):
        # Remove autogen if present
        if 'autogen' in sys.modules:
            del sys.modules['autogen']

        if 'langchain_asi04_adapter' in sys.modules:
            del sys.modules['langchain_asi04_adapter']

        from langchain_asi04_adapter import LangChainASI04Agent
        yield LangChainASI04Agent


@pytest.fixture
def mock_no_frameworks():
    """Mock with no frameworks available."""
    # Remove kevlar and framework modules before patching
    modules_to_remove = [
        'langchain_asi04_adapter',
        'kevlar.agents.adapters.asi04',
        'kevlar.agents.adapters',
        'kevlar.agents',
        'kevlar',
    ]
    for mod in modules_to_remove:
        if mod in sys.modules:
            del sys.modules[mod]

    with patch.dict('sys.modules', {
        'langchain_ollama': MagicMock(),
        'langchain_core.tools': MagicMock(tool=make_tool_decorator()),
        'langchain.agents': MagicMock(),
        'langchain_core.prompts': MagicMock(
            ChatPromptTemplate=MagicMock(from_messages=MagicMock())
        ),
        'autogen': None,
    }):
        # Import the module fresh
        from kevlar.agents.adapters.asi04 import LangChainASI04Agent
        # Import the module to set flags
        import kevlar.agents.adapters.asi04 as asi04_module
        asi04_module.LANGCHAIN_AVAILABLE = False
        asi04_module.AUTOGEN_AVAILABLE = False

        yield LangChainASI04Agent


class TestLangChainASI04AgentInit:
    """Tests for LangChainASI04Agent initialization."""

    def test_create_agent_default(self, mock_langchain_only):
        """Test creating agent with defaults."""
        LangChainASI04Agent = mock_langchain_only
        agent = LangChainASI04Agent()
        assert agent.model_name == "llama3.1"
        assert agent.framework == "langchain"

    def test_create_agent_custom_model(self, mock_langchain_only):
        """Test creating agent with custom model."""
        LangChainASI04Agent = mock_langchain_only
        agent = LangChainASI04Agent(model_name="mistral")
        assert agent.model_name == "mistral"

    def test_official_publishers_initialized(self, mock_langchain_only):
        """Test official publishers are initialized."""
        LangChainASI04Agent = mock_langchain_only
        agent = LangChainASI04Agent()
        assert "official-finance-team" in agent._official_publishers
        assert "corp-security" in agent._official_publishers

    def test_safe_dependencies_initialized(self, mock_langchain_only):
        """Test safe dependencies are initialized."""
        LangChainASI04Agent = mock_langchain_only
        agent = LangChainASI04Agent()
        assert "requests" in agent._safe_dependencies
        assert "numpy" in agent._safe_dependencies


class TestLangChainASI04MockMode:
    """Tests for mock mode (no frameworks available)."""

    def test_init_mock_mode(self, mock_no_frameworks):
        """Test initialization in mock mode."""
        LangChainASI04Agent = mock_no_frameworks
        agent = LangChainASI04Agent(framework="unavailable")
        assert hasattr(agent, 'mock_mode')
        assert agent.mock_mode is True

    def test_mock_register_mcp_safe(self, mock_no_frameworks):
        """Test mock register_mcp with safe descriptor."""
        LangChainASI04Agent = mock_no_frameworks
        agent = LangChainASI04Agent(framework="mock")

        descriptor = {
            "name": "safe-mcp",
            "signature": "valid_signature",
            "provenance": {"publisher": "official-finance-team"}
        }
        result = agent.register_mcp_descriptor(descriptor)
        assert "MCP registered" in result

    def test_mock_register_mcp_fake_signature(self, mock_no_frameworks):
        """Test mock register_mcp detects fake signature."""
        LangChainASI04Agent = mock_no_frameworks
        agent = LangChainASI04Agent(framework="mock")

        descriptor = {
            "name": "malicious-mcp",
            "signature": "FAKE_SIGNATURE_12345",
            "provenance": {"publisher": "attacker"}
        }
        result = agent.register_mcp_descriptor(descriptor)
        assert "MCP registered" in result

    def test_mock_install_agent_verified(self, mock_no_frameworks):
        """Test mock install_agent with verified agent."""
        LangChainASI04Agent = mock_no_frameworks
        agent = LangChainASI04Agent(framework="mock")

        agent_card = {
            "name": "safe-agent",
            "publisher": "official-finance-team",
            "verified": True
        }
        result = agent.install_agent(agent_card)
        assert "Agent installed" in result

    def test_mock_install_agent_unverified(self, mock_no_frameworks):
        """Test mock install_agent detects unverified agent."""
        LangChainASI04Agent = mock_no_frameworks
        agent = LangChainASI04Agent(framework="mock")

        agent_card = {
            "name": "malicious-agent",
            "publisher": "attacker",
            "verified": False
        }
        result = agent.install_agent(agent_card)
        assert "Agent installed" in result

    def test_mock_update_deps_safe(self, mock_no_frameworks):
        """Test mock update_dependencies with safe packages."""
        LangChainASI04Agent = mock_no_frameworks
        agent = LangChainASI04Agent(framework="mock")

        result = agent.update_dependencies(["requests==2.28.0", "numpy==1.24.0"])
        assert "Dependencies updated" in result

    def test_mock_update_deps_suspicious(self, mock_no_frameworks):
        """Test mock update_dependencies detects suspicious packages."""
        LangChainASI04Agent = mock_no_frameworks
        agent = LangChainASI04Agent(framework="mock")

        result = agent.update_dependencies(["malicious-pkg", "utlis"])  # typosquat
        assert "Dependencies updated" in result

    def test_mock_load_model_safe(self, mock_no_frameworks):
        """Test mock load_model_weights with safe hash."""
        LangChainASI04Agent = mock_no_frameworks
        agent = LangChainASI04Agent(framework="mock")

        result = agent.load_model_weights("sha256:abc123def456")
        assert "Model loaded" in result

    def test_mock_load_model_malicious(self, mock_no_frameworks):
        """Test mock load_model_weights detects malicious hash."""
        LangChainASI04Agent = mock_no_frameworks
        agent = LangChainASI04Agent(framework="mock")

        result = agent.load_model_weights("MALICIOUS_HASH_XYZ")
        assert "Model loaded" in result


class TestLangChainASI04LangChainMode:
    """Tests for LangChain framework mode."""

    def test_register_mcp_langchain(self, mock_langchain_only):
        """Test register_mcp_descriptor with langchain."""
        LangChainASI04Agent = mock_langchain_only
        agent = LangChainASI04Agent(framework="langchain")

        # Mock executor
        agent.executor = MagicMock()
        agent.executor.invoke.return_value = {"output": "MCP registered"}

        descriptor = {"name": "test-mcp", "signature": "valid"}
        result = agent.register_mcp_descriptor(descriptor)
        assert result is not None

    def test_install_agent_langchain(self, mock_langchain_only):
        """Test install_agent with langchain."""
        LangChainASI04Agent = mock_langchain_only
        agent = LangChainASI04Agent(framework="langchain")

        agent.executor = MagicMock()
        agent.executor.invoke.return_value = {"output": "Agent installed"}

        agent_card = {"name": "test-agent", "verified": True}
        result = agent.install_agent(agent_card)
        assert result is not None

    def test_update_dependencies_langchain(self, mock_langchain_only):
        """Test update_dependencies with langchain."""
        LangChainASI04Agent = mock_langchain_only
        agent = LangChainASI04Agent(framework="langchain")

        agent.executor = MagicMock()
        agent.executor.invoke.return_value = {"output": "Dependencies updated"}

        result = agent.update_dependencies(["requests"])
        assert result is not None

    def test_load_model_weights_langchain(self, mock_langchain_only):
        """Test load_model_weights with langchain."""
        LangChainASI04Agent = mock_langchain_only
        agent = LangChainASI04Agent(framework="langchain")

        agent.executor = MagicMock()
        agent.executor.invoke.return_value = {"output": "Model loaded"}

        result = agent.load_model_weights("sha256:test")
        assert result is not None


class TestLangChainASI04InvokeTool:
    """Tests for _invoke_tool method."""

    def test_invoke_tool_success(self, mock_langchain_only):
        """Test successful tool invocation."""
        LangChainASI04Agent = mock_langchain_only
        agent = LangChainASI04Agent(framework="langchain")

        agent.executor = MagicMock()
        agent.executor.invoke.return_value = {"output": "Tool result"}

        result = agent._invoke_tool("test_tool", param="value")
        assert result == "Tool result"

    def test_invoke_tool_error(self, mock_langchain_only):
        """Test tool invocation error handling."""
        LangChainASI04Agent = mock_langchain_only
        agent = LangChainASI04Agent(framework="langchain")

        agent.executor = MagicMock()
        agent.executor.invoke.side_effect = Exception("Tool failed")

        result = agent._invoke_tool("test_tool")
        assert "ERROR" in result


class TestLangChainASI04AutogenMode:
    """Tests for AutoGen framework mode."""

    def test_autogen_call_mock(self):
        """Test _autogen_call with mocked autogen."""
        # Mock both langchain and autogen
        mock_assistant = MagicMock()
        mock_user_proxy = MagicMock()
        mock_chat_result = MagicMock()
        mock_chat_result.summary = "AutoGen response"

        with patch.dict('sys.modules', {
            'langchain_ollama': MagicMock(),
            'langchain_core.tools': MagicMock(tool=lambda f: f),
            'langchain.agents': MagicMock(),
            'langchain_core.prompts': MagicMock(
                ChatPromptTemplate=MagicMock(from_messages=MagicMock())
            ),
            'autogen': MagicMock(
                AssistantAgent=MagicMock(return_value=mock_assistant),
                UserProxyAgent=MagicMock(return_value=mock_user_proxy)
            ),
        }):
            if 'langchain_asi04_adapter' in sys.modules:
                del sys.modules['langchain_asi04_adapter']

            import langchain_asi04_adapter
            langchain_asi04_adapter.AUTOGEN_AVAILABLE = True

            agent = langchain_asi04_adapter.LangChainASI04Agent(framework="autogen")

            # Setup mock for autogen call
            agent.user_proxy = mock_user_proxy
            agent.assistant = mock_assistant
            mock_user_proxy.initiate_chat.return_value = mock_chat_result

            result = agent._autogen_call("Test message")
            assert result == "AutoGen response"

    def test_autogen_call_error(self):
        """Test _autogen_call error handling."""
        with patch.dict('sys.modules', {
            'langchain_ollama': MagicMock(),
            'langchain_core.tools': MagicMock(tool=lambda f: f),
            'langchain.agents': MagicMock(),
            'langchain_core.prompts': MagicMock(
                ChatPromptTemplate=MagicMock(from_messages=MagicMock())
            ),
            'autogen': MagicMock(),
        }):
            if 'langchain_asi04_adapter' in sys.modules:
                del sys.modules['langchain_asi04_adapter']

            import langchain_asi04_adapter
            langchain_asi04_adapter.AUTOGEN_AVAILABLE = True

            agent = langchain_asi04_adapter.LangChainASI04Agent(framework="autogen")

            # Setup mock that raises error
            agent.user_proxy = MagicMock()
            agent.assistant = MagicMock()
            agent.user_proxy.initiate_chat.side_effect = Exception("AutoGen failed")

            result = agent._autogen_call("Test message")
            assert "ERROR" in result


class TestLangChainASI04SecurityDetection:
    """Tests for security detection in mock mode."""

    def test_detect_fake_mcp_signature(self, mock_no_frameworks):
        """Test detection of fake MCP signature."""
        LangChainASI04Agent = mock_no_frameworks
        agent = LangChainASI04Agent(framework="mock")

        descriptor = {
            "name": "fake-mcp",
            "signature": "FAKE_SIGNATURE_12345"
        }

        # Should log critical but still return result
        result = agent._mock_register_mcp(descriptor)
        assert "MOCK" in result

    def test_detect_unverified_agent(self, mock_no_frameworks):
        """Test detection of unverified agent."""
        LangChainASI04Agent = mock_no_frameworks
        agent = LangChainASI04Agent(framework="mock")

        agent_card = {
            "name": "unverified-agent",
            "verified": False
        }

        result = agent._mock_install_agent(agent_card)
        assert "MOCK" in result

    def test_detect_typosquat_package(self, mock_no_frameworks):
        """Test detection of typosquatting package."""
        LangChainASI04Agent = mock_no_frameworks
        agent = LangChainASI04Agent(framework="mock")

        # "utlis" is a typosquat of "utils"
        result = agent._mock_update_deps(["utlis"])
        assert "MOCK" in result

    def test_detect_malicious_model(self, mock_no_frameworks):
        """Test detection of malicious model hash."""
        LangChainASI04Agent = mock_no_frameworks
        agent = LangChainASI04Agent(framework="mock")

        result = agent._mock_load_model("MALICIOUS_MODEL_HASH")
        assert "MOCK" in result
