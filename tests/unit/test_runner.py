"""
Unit tests for runner module.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock
from datetime import datetime


class TestColors:
    """Tests for color constants."""

    def test_colors_defined(self):
        """Test that color constants are defined."""
        from kevlar.cli import COLORS
        assert "RED" in COLORS
        assert "GREEN" in COLORS
        assert "YELLOW" in COLORS
        assert "RESET" in COLORS
        assert "BOLD" in COLORS

    def test_colors_are_ansi_codes(self):
        """Test that colors are ANSI escape codes."""
        from kevlar.cli import COLORS
        for color in COLORS.values():
            assert color.startswith("\033[")


class TestPrintBanner:
    """Tests for print_banner function."""

    def test_print_banner_no_error(self, capsys):
        """Test that print_banner executes without error."""
        from kevlar.cli import print_banner
        print_banner()
        captured = capsys.readouterr()
        assert "Kevlar" in captured.out

    def test_banner_contains_version(self, capsys):
        """Test that banner contains version info."""
        from kevlar.cli import print_banner
        print_banner()
        captured = capsys.readouterr()
        assert "Version" in captured.out or "1.0" in captured.out


class TestSelectAsis:
    """Tests for select_asis_interactive function."""

    def test_select_all_asis(self, monkeypatch):
        """Test selecting all ASIs."""
        from kevlar.cli import select_asis_interactive
        monkeypatch.setattr('builtins.input', lambda _: 'all')
        result = select_asis_interactive()
        assert len(result) == 10
        assert "ASI01" in result
        assert "ASI10" in result

    def test_select_single_asi(self, monkeypatch):
        """Test selecting single ASI by number."""
        from kevlar.cli import select_asis_interactive
        monkeypatch.setattr('builtins.input', lambda _: '1')
        result = select_asis_interactive()
        assert result == ["ASI01"]

    def test_select_multiple_asis(self, monkeypatch):
        """Test selecting multiple ASIs."""
        from kevlar.cli import select_asis_interactive
        monkeypatch.setattr('builtins.input', lambda _: '1,2,3')
        result = select_asis_interactive()
        assert result == ["ASI01", "ASI02", "ASI03"]

    def test_select_custom_asis(self, monkeypatch):
        """Test custom ASI selection."""
        from kevlar.cli import select_asis_interactive
        inputs = iter(['custom', '1', '5', '0'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        result = select_asis_interactive()
        assert "ASI01" in result
        assert "ASI05" in result

    def test_invalid_input_defaults_to_asi01(self, monkeypatch):
        """Test invalid input defaults to ASI01."""
        from kevlar.cli import select_asis_interactive
        monkeypatch.setattr('builtins.input', lambda _: 'invalid')
        result = select_asis_interactive()
        assert result == ["ASI01"]


class TestSelectMode:
    """Tests for select_mode_interactive function."""

    def test_select_mock_mode(self, monkeypatch):
        """Test selecting mock mode."""
        from kevlar.cli import select_mode_interactive
        monkeypatch.setattr('builtins.input', lambda _: '1')
        result = select_mode_interactive()
        assert result == "mock"

    def test_select_real_mode(self, monkeypatch):
        """Test selecting real mode."""
        from kevlar.cli import select_mode_interactive
        monkeypatch.setattr('builtins.input', lambda _: '2')
        result = select_mode_interactive()
        assert result == "real"

    def test_invalid_mode_retries(self, monkeypatch):
        """Test invalid mode selection retries."""
        from kevlar.cli import select_mode_interactive
        inputs = iter(['invalid', '1'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        result = select_mode_interactive()
        assert result == "mock"


class TestCreateAgent:
    """Tests for create_agent function."""

    def test_create_mock_agent(self):
        """Test creating mock agent."""
        from kevlar.cli import create_agent
        from kevlar.agents import MockCopilotAgent
        agent = create_agent("mock")
        assert isinstance(agent, MockCopilotAgent)

    def test_create_real_agent(self):
        """Test creating real agent."""
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


class TestRunAsiTest:
    """Tests for run_asi_test function."""

    def test_run_asi01_test(self, mock_agent, default_config):
        """Test running ASI01 test."""
        from kevlar.cli import run_asi_test
        results = {}
        run_asi_test("ASI01", mock_agent, results)
        assert "ASI01" in results
        assert "vulnerable_count" in results["ASI01"]
        assert "total_count" in results["ASI01"]
        assert "duration" in results["ASI01"]

    def test_run_asi02_test(self, mock_agent, default_config):
        """Test running ASI02 test."""
        from kevlar.cli import run_asi_test
        results = {}
        run_asi_test("ASI02", mock_agent, results)
        assert "ASI02" in results

    def test_run_asi03_test(self, mock_agent, default_config):
        """Test running ASI03 test."""
        from kevlar.cli import run_asi_test
        results = {}
        run_asi_test("ASI03", mock_agent, results)
        assert "ASI03" in results

    def test_run_asi04_test(self, mock_agent, default_config):
        """Test running ASI04 test."""
        from kevlar.cli import run_asi_test
        results = {}
        run_asi_test("ASI04", mock_agent, results)
        assert "ASI04" in results

    def test_run_asi05_test(self, mock_agent, default_config):
        """Test running ASI05 test."""
        from kevlar.cli import run_asi_test
        results = {}
        run_asi_test("ASI05", mock_agent, results)
        assert "ASI05" in results

    def test_run_asi06_test(self, mock_agent, default_config):
        """Test running ASI06 test."""
        from kevlar.cli import run_asi_test
        results = {}
        run_asi_test("ASI06", mock_agent, results)
        assert "ASI06" in results

    def test_run_asi07_test(self, mock_agent, default_config):
        """Test running ASI07 test."""
        from kevlar.cli import run_asi_test
        results = {}
        run_asi_test("ASI07", mock_agent, results)
        assert "ASI07" in results

    def test_run_asi08_test(self, mock_agent, default_config):
        """Test running ASI08 test."""
        from kevlar.cli import run_asi_test
        results = {}
        run_asi_test("ASI08", mock_agent, results)
        assert "ASI08" in results

    def test_run_asi09_test(self, mock_agent, default_config):
        """Test running ASI09 test."""
        from kevlar.cli import run_asi_test
        results = {}
        run_asi_test("ASI09", mock_agent, results)
        assert "ASI09" in results

    def test_run_asi10_test(self, mock_agent, default_config):
        """Test running ASI10 test."""
        from kevlar.cli import run_asi_test
        results = {}
        run_asi_test("ASI10", mock_agent, results)
        assert "ASI10" in results

    def test_run_unknown_asi_handles_error(self, mock_agent):
        """Test running unknown ASI handles error gracefully."""
        from kevlar.cli import run_asi_test
        results = {}
        run_asi_test("ASI99", mock_agent, results)
        assert "ASI99" in results
        assert "error" in results["ASI99"]

    def test_run_test_records_duration(self, mock_agent):
        """Test that run_asi_test records duration."""
        from kevlar.cli import run_asi_test
        results = {}
        run_asi_test("ASI01", mock_agent, results)
        assert results["ASI01"]["duration"] >= 0


class TestGenerateAivssReport:
    """Tests for generate_aivss_report function."""

    def test_generate_report_creates_file(self, tmp_path, monkeypatch):
        """Test that report generation creates a file."""
        from kevlar.cli import generate_aivss_report
        monkeypatch.chdir(tmp_path)
        results = {
            "ASI01": {
                "vulnerable_count": 1,
                "total_count": 4,
                "duration": 1.5,
                "results": [
                    {"scenario": "EchoLeak", "vulnerable": True, "severity": "CRITICAL", "evidence": "test"}
                ],
            }
        }
        filename = generate_aivss_report(results, "mock")
        assert os.path.exists(filename)

    def test_report_contains_required_fields(self, tmp_path, monkeypatch):
        """Test that report contains required AIVSS fields."""
        from kevlar.cli import generate_aivss_report
        monkeypatch.chdir(tmp_path)
        results = {
            "ASI01": {
                "vulnerable_count": 0,
                "total_count": 4,
                "duration": 1.0,
                "results": [],
            }
        }
        filename = generate_aivss_report(results, "mock")
        with open(filename) as f:
            report = json.load(f)

        assert "aivss_version" in report
        assert "benchmark" in report
        assert "agent" in report
        assert "scan" in report
        assert "findings" in report

    def test_report_counts_vulnerabilities(self, tmp_path, monkeypatch):
        """Test that report correctly counts vulnerabilities."""
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
                ],
            },
            "ASI02": {
                "vulnerable_count": 1,
                "total_count": 3,
                "duration": 0.5,
                "results": [
                    {"scenario": "C", "vulnerable": True, "severity": "MEDIUM", "evidence": "test"},
                ],
            },
        }
        filename = generate_aivss_report(results, "mock")
        with open(filename) as f:
            report = json.load(f)

        assert report["scan"]["total_vulnerabilities"] == 3
        assert report["scan"]["critical_vulnerabilities"] == 1
        assert report["scan"]["high_vulnerabilities"] == 1
        assert report["scan"]["medium_vulnerabilities"] == 1

    def test_report_handles_errors(self, tmp_path, monkeypatch):
        """Test that report handles ASI results with errors."""
        from kevlar.cli import generate_aivss_report
        monkeypatch.chdir(tmp_path)
        results = {
            "ASI01": {
                "error": "Test error",
                "duration": 0.1,
            }
        }
        filename = generate_aivss_report(results, "mock")
        assert os.path.exists(filename)

    def test_report_records_agent_mode(self, tmp_path, monkeypatch):
        """Test that report records agent mode correctly."""
        from kevlar.cli import generate_aivss_report
        monkeypatch.chdir(tmp_path)
        results = {"ASI01": {"vulnerable_count": 0, "total_count": 0, "duration": 0.1, "results": []}}

        filename = generate_aivss_report(results, "real")
        with open(filename) as f:
            report = json.load(f)
        assert report["agent"]["mode"] == "real"
        assert "llama" in report["agent"]["model"]

    def test_report_json_format(self, tmp_path, monkeypatch):
        """Test that report is valid JSON."""
        from kevlar.cli import generate_aivss_report
        monkeypatch.chdir(tmp_path)
        results = {"ASI01": {"vulnerable_count": 0, "total_count": 0, "duration": 0.1, "results": []}}
        filename = generate_aivss_report(results, "mock")

        with open(filename) as f:
            report = json.load(f)
        assert isinstance(report, dict)


class TestReportDirectory:
    """Tests for report directory creation."""

    def test_creates_reports_directory(self, tmp_path, monkeypatch):
        """Test that reports directory is created if not exists."""
        from kevlar.cli import generate_aivss_report
        monkeypatch.chdir(tmp_path)
        results = {"ASI01": {"vulnerable_count": 0, "total_count": 0, "duration": 0.1, "results": []}}
        generate_aivss_report(results, "mock")
        assert os.path.exists(tmp_path / "reports")

    def test_uses_existing_reports_directory(self, tmp_path, monkeypatch):
        """Test that existing reports directory is used."""
        from kevlar.cli import generate_aivss_report
        monkeypatch.chdir(tmp_path)
        (tmp_path / "reports").mkdir()
        results = {"ASI01": {"vulnerable_count": 0, "total_count": 0, "duration": 0.1, "results": []}}
        filename = generate_aivss_report(results, "mock")
        assert filename.startswith("reports/")


class TestReportTimestamp:
    """Tests for report timestamp handling."""

    def test_report_filename_has_timestamp(self, tmp_path, monkeypatch):
        """Test that report filename includes timestamp."""
        from kevlar.cli import generate_aivss_report
        monkeypatch.chdir(tmp_path)
        results = {"ASI01": {"vulnerable_count": 0, "total_count": 0, "duration": 0.1, "results": []}}
        filename = generate_aivss_report(results, "mock")
        # Filename should contain date pattern
        assert "kevlar_aivss_report_" in filename
        assert ".json" in filename

    def test_report_contains_timestamps(self, tmp_path, monkeypatch):
        """Test that report contains start and end timestamps."""
        from kevlar.cli import generate_aivss_report
        monkeypatch.chdir(tmp_path)
        results = {"ASI01": {"vulnerable_count": 0, "total_count": 0, "duration": 0.1, "results": []}}
        filename = generate_aivss_report(results, "mock")

        with open(filename) as f:
            report = json.load(f)
        assert "start_time" in report["scan"]
        assert "end_time" in report["scan"]
