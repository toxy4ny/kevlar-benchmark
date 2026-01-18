"""
Unit tests for agent dependency checking and strict mode failures.
"""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from kevlar.agents import (
    check_langchain_available,
    check_ollama_available,
    check_real_agent_dependencies,
)
from kevlar.cli import create_agent, check_dependencies_and_exit, main


class TestCheckLangchainAvailable:
    """Tests for check_langchain_available function."""

    def test_returns_bool(self):
        """Test that function returns a boolean."""
        result = check_langchain_available()
        assert isinstance(result, bool)

    def test_returns_langchain_available_value(self):
        """Test that function returns LANGCHAIN_AVAILABLE value."""
        from kevlar.agents.langchain import LANGCHAIN_AVAILABLE
        assert check_langchain_available() == LANGCHAIN_AVAILABLE


class TestCheckOllamaAvailable:
    """Tests for check_ollama_available function."""

    def test_returns_bool(self):
        """Test that function returns a boolean."""
        result = check_ollama_available()
        assert isinstance(result, bool)

    def test_returns_false_when_ollama_not_running(self):
        """Test that function returns False when Ollama is not running."""
        # Use non-existent port
        result = check_ollama_available("http://localhost:99999")
        assert result is False

    def test_returns_false_on_timeout(self):
        """Test that function returns False on connection timeout."""
        # Mock urllib.request.urlopen to raise timeout
        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_urlopen.side_effect = TimeoutError()
            result = check_ollama_available()
            assert result is False

    def test_returns_true_when_ollama_responds(self):
        """Test that function returns True when Ollama responds with 200."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch('urllib.request.urlopen', return_value=mock_response):
            result = check_ollama_available()
            assert result is True

    def test_returns_false_on_non_200_status(self):
        """Test that function returns False on non-200 status."""
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch('urllib.request.urlopen', return_value=mock_response):
            result = check_ollama_available()
            # Note: current implementation only checks status == 200
            assert result is False


class TestCheckRealAgentDependencies:
    """Tests for check_real_agent_dependencies function."""

    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        result = check_real_agent_dependencies()
        assert isinstance(result, dict)

    def test_dict_has_required_keys(self):
        """Test that returned dict has all required keys."""
        result = check_real_agent_dependencies()
        assert 'langchain' in result
        assert 'ollama' in result
        assert 'available' in result
        assert 'missing' in result

    def test_available_is_true_when_all_deps_present(self):
        """Test that available is True when all dependencies present."""
        with patch('kevlar.agents.check_langchain_available', return_value=True), \
             patch('kevlar.agents.check_ollama_available', return_value=True):
            result = check_real_agent_dependencies()
            assert result['available'] is True
            assert result['langchain'] is True
            assert result['ollama'] is True
            assert result['missing'] == []

    def test_available_is_false_when_langchain_missing(self):
        """Test that available is False when LangChain is missing."""
        with patch('kevlar.agents.check_langchain_available', return_value=False), \
             patch('kevlar.agents.check_ollama_available', return_value=True):
            result = check_real_agent_dependencies()
            assert result['available'] is False
            assert result['langchain'] is False
            assert result['ollama'] is True
            assert len(result['missing']) == 1
            assert 'langchain' in result['missing'][0]

    def test_available_is_false_when_ollama_missing(self):
        """Test that available is False when Ollama is missing."""
        with patch('kevlar.agents.check_langchain_available', return_value=True), \
             patch('kevlar.agents.check_ollama_available', return_value=False):
            result = check_real_agent_dependencies()
            assert result['available'] is False
            assert result['langchain'] is True
            assert result['ollama'] is False
            assert len(result['missing']) == 1
            assert 'ollama' in result['missing'][0]

    def test_available_is_false_when_both_missing(self):
        """Test that available is False when both dependencies missing."""
        with patch('kevlar.agents.check_langchain_available', return_value=False), \
             patch('kevlar.agents.check_ollama_available', return_value=False):
            result = check_real_agent_dependencies()
            assert result['available'] is False
            assert result['langchain'] is False
            assert result['ollama'] is False
            assert len(result['missing']) == 2


class TestCreateAgent:
    """Tests for create_agent function."""

    def test_mock_mode_always_works(self):
        """Test that mock mode always creates an agent."""
        agent = create_agent('mock')
        assert agent is not None
        from kevlar.agents import MockCopilotAgent
        assert isinstance(agent, MockCopilotAgent)

    def test_mock_mode_quiet(self):
        """Test that mock mode works in quiet mode."""
        agent = create_agent('mock', quiet=True)
        assert agent is not None

    def test_real_mode_raises_when_deps_unavailable(self):
        """Test that real mode raises ClickException when deps unavailable."""
        import click
        with patch('kevlar.agents.check_real_agent_dependencies') as mock_check:
            mock_check.return_value = {
                'langchain': False,
                'ollama': False,
                'available': False,
                'missing': ['langchain (pip install langchain langchain-ollama)']
            }
            with pytest.raises(click.ClickException) as exc_info:
                create_agent('real')
            assert 'Real agent mode requires' in str(exc_info.value.message)
            assert 'langchain' in str(exc_info.value.message)

    def test_real_mode_error_message_includes_mock_suggestion(self):
        """Test that error message suggests using mock mode."""
        import click
        with patch('kevlar.agents.check_real_agent_dependencies') as mock_check:
            mock_check.return_value = {
                'langchain': False,
                'ollama': False,
                'available': False,
                'missing': ['langchain (pip install langchain langchain-ollama)']
            }
            with pytest.raises(click.ClickException) as exc_info:
                create_agent('real')
            assert '--mode mock' in str(exc_info.value.message)

    def test_real_mode_works_when_deps_available(self):
        """Test that real mode creates agent when dependencies available."""
        with patch('kevlar.agents.check_real_agent_dependencies') as mock_check:
            mock_check.return_value = {
                'langchain': True,
                'ollama': True,
                'available': True,
                'missing': []
            }
            # Mock the RealLangChainAgent to avoid actual LangChain initialization
            with patch('kevlar.cli.RealLangChainAgent') as mock_agent_class:
                mock_agent = MagicMock()
                mock_agent_class.return_value = mock_agent
                agent = create_agent('real', model='test-model', quiet=True)
                assert agent == mock_agent
                mock_agent_class.assert_called_once_with(model_name='test-model')


class TestCheckDependenciesAndExit:
    """Tests for check_dependencies_and_exit function."""

    def test_exits_with_0_when_all_deps_available(self):
        """Test that function exits with code 0 when all dependencies available."""
        with patch('kevlar.agents.check_real_agent_dependencies') as mock_check:
            mock_check.return_value = {
                'langchain': True,
                'ollama': True,
                'available': True,
                'missing': []
            }
            with pytest.raises(SystemExit) as exc_info:
                check_dependencies_and_exit(quiet=True)
            assert exc_info.value.code == 0

    def test_exits_with_1_when_deps_missing(self):
        """Test that function exits with code 1 when dependencies missing."""
        with patch('kevlar.agents.check_real_agent_dependencies') as mock_check:
            mock_check.return_value = {
                'langchain': False,
                'ollama': False,
                'available': False,
                'missing': ['langchain', 'ollama']
            }
            with pytest.raises(SystemExit) as exc_info:
                check_dependencies_and_exit(quiet=True)
            assert exc_info.value.code == 1

    def test_prints_status_output(self, capsys):
        """Test that function prints status output."""
        with patch('kevlar.agents.check_real_agent_dependencies') as mock_check:
            mock_check.return_value = {
                'langchain': True,
                'ollama': False,
                'available': False,
                'missing': ['ollama (not running at http://localhost:11434)']
            }
            with pytest.raises(SystemExit):
                check_dependencies_and_exit(quiet=False)
            captured = capsys.readouterr()
            assert 'LangChain' in captured.out
            assert 'Ollama' in captured.out


class TestCheckCLIOption:
    """Tests for --check CLI option."""

    def test_check_option_exists(self):
        """Test that --check option is recognized."""
        runner = CliRunner()
        # Use --help to verify option exists
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert '--check' in result.output

    def test_check_option_runs_dependency_check(self):
        """Test that --check option runs dependency check."""
        runner = CliRunner()
        with patch('kevlar.cli.check_dependencies_and_exit') as mock_check:
            mock_check.side_effect = SystemExit(0)
            result = runner.invoke(main, ['--check'])
            mock_check.assert_called_once()

    def test_check_option_respects_quiet_flag(self):
        """Test that --check option respects --quiet flag."""
        runner = CliRunner()
        with patch('kevlar.cli.check_dependencies_and_exit') as mock_check:
            mock_check.side_effect = SystemExit(0)
            runner.invoke(main, ['--check', '--quiet'])
            mock_check.assert_called_once_with(True)

    def test_check_returns_exit_code_0_when_deps_available(self):
        """Test that --check returns exit code 0 when deps available."""
        runner = CliRunner()
        with patch('kevlar.agents.check_real_agent_dependencies') as mock_deps:
            mock_deps.return_value = {
                'langchain': True,
                'ollama': True,
                'available': True,
                'missing': []
            }
            result = runner.invoke(main, ['--check'])
            assert result.exit_code == 0

    def test_check_returns_exit_code_1_when_deps_missing(self):
        """Test that --check returns exit code 1 when deps missing."""
        runner = CliRunner()
        with patch('kevlar.agents.check_real_agent_dependencies') as mock_deps:
            mock_deps.return_value = {
                'langchain': False,
                'ollama': False,
                'available': False,
                'missing': ['langchain', 'ollama']
            }
            result = runner.invoke(main, ['--check'])
            assert result.exit_code == 1


class TestRealModeFailsWithoutDeps:
    """Integration tests for real mode failing when deps unavailable."""

    def test_real_mode_cli_fails_gracefully(self):
        """Test that CLI fails gracefully when real mode deps unavailable."""
        runner = CliRunner()
        with patch('kevlar.agents.check_real_agent_dependencies') as mock_deps:
            mock_deps.return_value = {
                'langchain': False,
                'ollama': False,
                'available': False,
                'missing': [
                    'langchain (pip install langchain langchain-ollama)',
                    'ollama (not running at http://localhost:11434)'
                ]
            }
            result = runner.invoke(main, ['--asi', 'ASI01', '--mode', 'real'])
            assert result.exit_code != 0
            assert 'Real agent mode requires' in result.output

    def test_mock_mode_cli_always_works(self):
        """Test that mock mode always works via CLI."""
        runner = CliRunner()
        # Just test that command starts without error
        # Full execution would take too long for unit test
        with patch('kevlar.cli.run_noninteractive_mode', return_value=0):
            result = runner.invoke(main, ['--asi', 'ASI01', '--mode', 'mock'])
            assert result.exit_code == 0
