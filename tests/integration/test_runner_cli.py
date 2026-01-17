"""
Integration tests for runner CLI.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock


class TestRunnerCLIFlow:
    """Integration tests for CLI runner flow."""

    def test_full_mock_agent_run(self, tmp_path, monkeypatch):
        """Test full run with mock agent."""
        from runner import run_asi_test, generate_aivss_report, create_agent

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
        from runner import run_asi_test, generate_aivss_report, create_agent

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
        from runner import run_asi_test, generate_aivss_report, create_agent

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
        from runner import create_agent
        from local_agent import MockCopilotAgent

        agent = create_agent("mock")
        assert isinstance(agent, MockCopilotAgent)

    def test_real_agent_selection(self):
        """Test creating real agent with mocked dependencies."""
        from runner import create_agent

        with patch.dict('sys.modules', {
            'langchain_ollama': MagicMock(),
            'langchain_core.tools': MagicMock(),
            'langchain.agents': MagicMock(),
            'langchain_core.prompts': MagicMock(),
        }):
            agent = create_agent("real")
            assert agent is not None


class TestResultsAggregation:
    """Tests for results aggregation."""

    def test_vulnerability_counting(self, tmp_path, monkeypatch):
        """Test vulnerability counting in report."""
        from runner import generate_aivss_report

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
        from runner import generate_aivss_report

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
        from runner import run_asi_test, generate_aivss_report, create_agent
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
