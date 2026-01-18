"""
Integration tests for runner CLI.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock

from click.testing import CliRunner


class TestRunnerCLIFlow:
    """Integration tests for CLI runner flow."""

    def test_full_mock_agent_run(self, tmp_path, monkeypatch):
        """Test full run with mock agent."""
        from kevlar.cli import run_asi_test, generate_aivss_report, create_agent

        monkeypatch.chdir(tmp_path)

        # Create mock agent
        agent = create_agent("mock")

        # Run a few ASI tests
        results = {}
        run_asi_test("ASI01", agent, results)
        run_asi_test("ASI02", agent, results)

        # Generate report
        report_file = generate_aivss_report(results, "mock")

        # Verify report exists and is valid
        assert os.path.exists(report_file)
        with open(report_file) as f:
            report = json.load(f)

        assert "ASI01" in report["scan"]["tested_asis"]
        assert "ASI02" in report["scan"]["tested_asis"]
        assert len(report["findings"]) >= 0

    def test_all_asi_tests_sequential(self, tmp_path, monkeypatch):
        """Test running all ASI tests sequentially."""
        from kevlar.cli import run_asi_test, generate_aivss_report, create_agent

        monkeypatch.chdir(tmp_path)

        agent = create_agent("mock")
        results = {}

        all_asis = [f"ASI{i:02d}" for i in range(1, 11)]
        for asi in all_asis:
            run_asi_test(asi, agent, results)

        # All should complete
        assert len(results) == 10

        # Generate report
        report_file = generate_aivss_report(results, "mock")
        assert os.path.exists(report_file)

    def test_report_format_compliance(self, tmp_path, monkeypatch):
        """Test that report format is AIVSS compliant."""
        from kevlar.cli import run_asi_test, generate_aivss_report, create_agent

        monkeypatch.chdir(tmp_path)

        agent = create_agent("mock")
        results = {}
        run_asi_test("ASI01", agent, results)

        report_file = generate_aivss_report(results, "mock")

        with open(report_file) as f:
            report = json.load(f)

        # Check AIVSS structure
        required_fields = ["aivss_version", "benchmark", "agent", "scan", "findings"]
        for field in required_fields:
            assert field in report, f"Missing required field: {field}"

        # Check benchmark info
        assert report["benchmark"]["name"] == "Kevlar"

        # Check scan info
        scan_fields = [
            "start_time", "end_time", "duration_seconds",
            "tested_asis", "total_vulnerabilities"
        ]
        for field in scan_fields:
            assert field in report["scan"]


class TestAgentSelection:
    """Tests for agent selection flow."""

    def test_mock_agent_selection(self):
        """Test creating mock agent."""
        from kevlar.cli import create_agent
        from kevlar.agents import MockCopilotAgent

        agent = create_agent("mock")
        assert isinstance(agent, MockCopilotAgent)

    def test_real_agent_selection(self):
        """Test creating real agent with mocked dependency check."""
        from kevlar.cli import create_agent

        with patch('kevlar.agents.check_real_agent_dependencies') as mock_deps:
            mock_deps.return_value = {
                'langchain': True,
                'ollama': True,
                'available': True,
                'missing': []
            }
            agent = create_agent("real", quiet=True)
            assert agent is not None


class TestResultsAggregation:
    """Tests for results aggregation."""

    def test_vulnerability_counting(self, tmp_path, monkeypatch):
        """Test vulnerability counting in report."""
        from kevlar.cli import generate_aivss_report

        monkeypatch.chdir(tmp_path)

        results = {
            "ASI01": {
                "vulnerable_count": 2,
                "total_count": 4,
                "duration": 1.0,
                "results": [
                    {"scenario": "A", "vulnerable": True, "severity": "CRITICAL", "evidence": "test"},
                    {"scenario": "B", "vulnerable": True, "severity": "HIGH", "evidence": "test"},
                    {"scenario": "C", "vulnerable": False, "severity": "NONE", "evidence": ""},
                    {"scenario": "D", "vulnerable": False, "severity": "NONE", "evidence": ""},
                ],
            },
        }

        report_file = generate_aivss_report(results, "mock")

        with open(report_file) as f:
            report = json.load(f)

        assert report["scan"]["total_vulnerabilities"] == 2
        assert report["scan"]["critical_vulnerabilities"] == 1
        assert report["scan"]["high_vulnerabilities"] == 1

    def test_error_handling_in_results(self, tmp_path, monkeypatch):
        """Test handling of errors in results."""
        from kevlar.cli import generate_aivss_report

        monkeypatch.chdir(tmp_path)

        results = {
            "ASI01": {
                "error": "Test error occurred",
                "duration": 0.5,
            },
            "ASI02": {
                "vulnerable_count": 1,
                "total_count": 9,
                "duration": 1.0,
                "results": [
                    {"scenario": "Test", "vulnerable": True, "severity": "CRITICAL", "evidence": "test"},
                ],
            },
        }

        report_file = generate_aivss_report(results, "mock")
        assert os.path.exists(report_file)

        with open(report_file) as f:
            report = json.load(f)

        # Only ASI02 should contribute to vulnerabilities
        assert report["scan"]["total_vulnerabilities"] == 1


class TestMultipleRuns:
    """Tests for multiple sequential runs."""

    def test_multiple_report_generation(self, tmp_path, monkeypatch):
        """Test generating multiple reports."""
        from kevlar.cli import run_asi_test, generate_aivss_report, create_agent
        import time

        monkeypatch.chdir(tmp_path)

        agent = create_agent("mock")

        # First run
        results1 = {}
        run_asi_test("ASI01", agent, results1)
        report1 = generate_aivss_report(results1, "mock")

        # Delay > 1 second to ensure different timestamp (seconds precision)
        time.sleep(1.1)

        # Second run
        results2 = {}
        run_asi_test("ASI02", agent, results2)
        report2 = generate_aivss_report(results2, "mock")

        # Both reports should exist and be different files
        assert os.path.exists(report1)
        assert os.path.exists(report2)
        assert report1 != report2


class TestClickCLI:
    """Tests for click-based CLI interface."""

    def test_help_option(self):
        """Test --help option displays usage info."""
        from kevlar.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ['--help'])

        assert result.exit_code == 0
        assert 'Kevlar' in result.output
        assert '--asi' in result.output
        assert '--all' in result.output
        assert '--mode' in result.output
        assert '--model' in result.output
        assert '--output' in result.output
        assert '--quiet' in result.output
        assert '--ci' in result.output

    def test_version_option(self):
        """Test --version option displays version."""
        from kevlar.cli import main, __version__

        runner = CliRunner()
        result = runner.invoke(main, ['--version'])

        assert result.exit_code == 0
        assert __version__ in result.output

    def test_single_asi_argument(self, tmp_path):
        """Test running with single --asi argument."""
        from kevlar.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, ['--asi', 'ASI01', '--mode', 'mock', '--quiet'])

            assert result.exit_code == 0

    def test_multiple_asi_arguments(self, tmp_path):
        """Test running with multiple --asi arguments."""
        from kevlar.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, ['--asi', 'ASI01', '--asi', 'ASI02', '--mode', 'mock', '--quiet'])

            assert result.exit_code == 0

    def test_all_flag(self, tmp_path):
        """Test running with --all flag."""
        from kevlar.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, ['--all', '--mode', 'mock', '--quiet'])

            assert result.exit_code == 0

    def test_invalid_asi_argument(self):
        """Test error on invalid ASI argument."""
        from kevlar.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ['--asi', 'ASI99', '--mode', 'mock'])

        assert result.exit_code != 0
        assert 'Unknown ASI' in result.output or 'ASI99' in result.output

    def test_case_insensitive_asi(self, tmp_path):
        """Test ASI arguments are case-insensitive."""
        from kevlar.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, ['--asi', 'asi01', '--mode', 'mock', '--quiet'])

            assert result.exit_code == 0

    def test_custom_output_path(self, tmp_path):
        """Test custom output path."""
        from kevlar.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            output_file = 'custom_report.json'
            result = runner.invoke(main, ['--asi', 'ASI01', '--mode', 'mock', '--quiet', '--output', output_file])

            assert result.exit_code == 0
            assert os.path.exists(output_file)

            with open(output_file) as f:
                report = json.load(f)
            assert 'ASI01' in report['scan']['tested_asis']

    def test_quiet_mode_no_banner(self, tmp_path):
        """Test quiet mode suppresses banner."""
        from kevlar.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, ['--asi', 'ASI01', '--mode', 'mock', '--quiet'])

            # Banner contains "KEVLAR" ASCII art
            assert 'KEVLAR' not in result.output.upper() or result.output == ''

    def test_mode_choice_validation(self):
        """Test mode option only accepts mock/real."""
        from kevlar.cli import main

        runner = CliRunner()
        result = runner.invoke(main, ['--asi', 'ASI01', '--mode', 'invalid'])

        assert result.exit_code != 0
        assert 'Invalid value' in result.output or 'invalid' in result.output.lower()


class TestCIModeExitCodes:
    """Tests for CI mode exit codes."""

    def test_ci_mode_exit_code_success(self, tmp_path):
        """Test CI mode returns 0 when no vulnerabilities."""
        from kevlar.cli import main, determine_exit_code

        # Test determine_exit_code directly with no vulns
        results = {
            "ASI01": {
                "vulnerable_count": 0,
                "total_count": 4,
                "duration": 1.0,
                "results": [
                    {"scenario": "A", "vulnerable": False, "severity": "NONE"},
                ],
            },
        }
        assert determine_exit_code(results) == 0

    def test_ci_mode_exit_code_vulns_found(self):
        """Test CI mode returns 1 when medium/high vulnerabilities found."""
        from kevlar.cli import determine_exit_code, EXIT_VULNS_FOUND

        results = {
            "ASI01": {
                "vulnerable_count": 1,
                "total_count": 4,
                "duration": 1.0,
                "results": [
                    {"scenario": "A", "vulnerable": True, "severity": "HIGH"},
                ],
            },
        }
        assert determine_exit_code(results) == EXIT_VULNS_FOUND

    def test_ci_mode_exit_code_critical(self):
        """Test CI mode returns 2 when critical vulnerabilities found."""
        from kevlar.cli import determine_exit_code, EXIT_CRITICAL_VULNS

        results = {
            "ASI01": {
                "vulnerable_count": 1,
                "total_count": 4,
                "duration": 1.0,
                "results": [
                    {"scenario": "A", "vulnerable": True, "severity": "CRITICAL"},
                ],
            },
        }
        assert determine_exit_code(results) == EXIT_CRITICAL_VULNS

    def test_ci_implies_quiet(self, tmp_path):
        """Test that --ci flag implies quiet mode."""
        from kevlar.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(main, ['--asi', 'ASI01', '--mode', 'mock', '--ci'])

            # CI mode should be quiet - no banner
            assert 'KEVLAR' not in result.output.upper() or result.output == ''


class TestParseASIArgs:
    """Tests for ASI argument parsing."""

    def test_parse_single_asi(self):
        """Test parsing single ASI argument."""
        from kevlar.cli import parse_asi_args

        result = parse_asi_args(('ASI01',))
        assert result == ['ASI01']

    def test_parse_multiple_asis(self):
        """Test parsing multiple ASI arguments."""
        from kevlar.cli import parse_asi_args

        result = parse_asi_args(('ASI01', 'ASI05', 'ASI10'))
        assert result == ['ASI01', 'ASI05', 'ASI10']

    def test_parse_lowercase_asi(self):
        """Test parsing lowercase ASI arguments."""
        from kevlar.cli import parse_asi_args

        result = parse_asi_args(('asi01', 'asi05'))
        assert result == ['ASI01', 'ASI05']

    def test_parse_mixed_case_asi(self):
        """Test parsing mixed case ASI arguments."""
        from kevlar.cli import parse_asi_args

        result = parse_asi_args(('Asi01', 'ASI05', 'asi10'))
        assert result == ['ASI01', 'ASI05', 'ASI10']

    def test_parse_deduplicate_asis(self):
        """Test that duplicate ASIs are removed."""
        from kevlar.cli import parse_asi_args

        result = parse_asi_args(('ASI01', 'ASI01', 'asi01'))
        assert result == ['ASI01']

    def test_parse_invalid_asi_raises(self):
        """Test that invalid ASI raises BadParameter."""
        from kevlar.cli import parse_asi_args
        import click

        with pytest.raises(click.BadParameter) as exc_info:
            parse_asi_args(('ASI99',))

        assert 'Unknown ASI' in str(exc_info.value)


class TestGetColors:
    """Tests for color helper function."""

    def test_get_colors_normal(self):
        """Test colors are returned in normal mode."""
        from kevlar.cli import get_colors, COLORS

        colors = get_colors(quiet=False)
        assert colors == COLORS
        assert colors['RED'] == '\033[91m'

    def test_get_colors_quiet(self):
        """Test colors are empty strings in quiet mode."""
        from kevlar.cli import get_colors

        colors = get_colors(quiet=True)
        assert all(v == '' for v in colors.values())


class TestNonInteractiveWithOutput:
    """Tests for non-interactive mode with custom output."""

    def test_output_directory_created(self, tmp_path):
        """Test output directory is created if it doesn't exist."""
        from kevlar.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            output_file = 'subdir/report.json'
            result = runner.invoke(main, ['--asi', 'ASI01', '--mode', 'mock', '--quiet', '--output', output_file])

            assert result.exit_code == 0
            assert os.path.exists(output_file)

    def test_report_contains_model_info(self, tmp_path):
        """Test report contains correct model info."""
        from kevlar.cli import main

        runner = CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            output_file = 'report.json'
            result = runner.invoke(main, ['--asi', 'ASI01', '--mode', 'mock', '--quiet', '--output', output_file])

            assert result.exit_code == 0

            with open(output_file) as f:
                report = json.load(f)

            assert report['agent']['mode'] == 'mock'
            assert report['agent']['model'] == 'MockCopilotAgent'
