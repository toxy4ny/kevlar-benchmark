"""
Integration tests for orchestrator pipeline.
"""

import pytest
from unittest.mock import MagicMock, patch

from local_agent import MockCopilotAgent
from kevlar_types import SessionLog


class TestOrchestratorPipeline:
    """Integration tests for full orchestrator pipeline."""

    def test_asi01_full_pipeline(self, mock_agent):
        """Test ASI01 full pipeline."""
        from modules.critical.asi01_goal_hijack import GoalHijackOrchestrator

        orchestrator = GoalHijackOrchestrator(mock_agent)
        results = orchestrator.run_all_scenarios()

        assert len(results) == 4
        for result in results:
            assert "scenario" in result
            assert "vulnerable" in result or "error" in result

    def test_asi02_full_pipeline(self, mock_agent):
        """Test ASI02 full pipeline."""
        from modules.critical.asi02_tool_abuse import ToolAbuseOrchestrator

        orchestrator = ToolAbuseOrchestrator(mock_agent)
        results = orchestrator.run_all_tests()

        assert len(results) == 9
        for result in results:
            assert "scenario" in result

    def test_asi03_full_pipeline(self, mock_agent):
        """Test ASI03 full pipeline."""
        from modules.critical.asi03_identity_abuse import IdentityOrchestrator

        orchestrator = IdentityOrchestrator(mock_agent)
        results = orchestrator.run_all_tests()

        assert len(results) == 5
        for result in results:
            assert "scenario" in result

    def test_asi04_full_pipeline(self, mock_agent):
        """Test ASI04 full pipeline."""
        from modules.critical.asi04_supply_chain import SupplyChainOrchestrator

        orchestrator = SupplyChainOrchestrator(mock_agent)
        results = orchestrator.run_all_tests()

        assert len(results) == 5
        for result in results:
            assert "scenario" in result

    def test_asi05_full_pipeline(self, mock_agent):
        """Test ASI05 full pipeline."""
        from modules.critical.asi05_rce.rce_orchestrator import RCEOrchestrator

        orchestrator = RCEOrchestrator(mock_agent)
        results = orchestrator.run_all_tests()

        assert len(results) == 8
        for result in results:
            assert "scenario" in result

    def test_asi06_full_pipeline(self, mock_agent):
        """Test ASI06 full pipeline."""
        from modules.high.asi06_memory_poisoning import MemoryPoisoningOrchestrator

        orchestrator = MemoryPoisoningOrchestrator(mock_agent)
        results = orchestrator.run_all_tests()

        assert len(results) == 4
        for result in results:
            assert "scenario" in result

    def test_asi07_full_pipeline(self, mock_agent):
        """Test ASI07 full pipeline."""
        from modules.high.asi07_inter_agent_comms import InterAgentOrchestrator

        orchestrator = InterAgentOrchestrator(mock_agent)
        results = orchestrator.run_all_tests()

        assert len(results) == 4
        for result in results:
            assert "scenario" in result

    def test_asi08_full_pipeline(self, mock_agent):
        """Test ASI08 full pipeline."""
        from modules.high.asi08_cascading_failures import CascadingOrchestrator

        orchestrator = CascadingOrchestrator(mock_agent)
        results = orchestrator.run_all_tests()

        assert len(results) == 3
        for result in results:
            assert "scenario" in result

    def test_asi09_full_pipeline(self, mock_agent):
        """Test ASI09 full pipeline."""
        from modules.medium.asi09_human_trust import HumanTrustOrchestrator

        orchestrator = HumanTrustOrchestrator(mock_agent)
        results = orchestrator.run_all_tests()

        assert len(results) == 3
        for result in results:
            assert "scenario" in result

    def test_asi10_full_pipeline(self, mock_agent):
        """Test ASI10 full pipeline."""
        from modules.medium.asi10_rogue_agents import RogueAgentOrchestrator

        orchestrator = RogueAgentOrchestrator(mock_agent)
        results = orchestrator.run_all_tests()

        assert len(results) == 3
        for result in results:
            assert "scenario" in result


class TestCrossModuleIntegration:
    """Tests for cross-module integration."""

    def test_all_orchestrators_with_same_agent(self, mock_agent):
        """Test all orchestrators work with same agent instance."""
        from modules.critical.asi01_goal_hijack import GoalHijackOrchestrator
        from modules.critical.asi02_tool_abuse import ToolAbuseOrchestrator
        from modules.critical.asi03_identity_abuse import IdentityOrchestrator

        # All orchestrators should work with same agent
        orchestrator1 = GoalHijackOrchestrator(mock_agent)
        orchestrator2 = ToolAbuseOrchestrator(mock_agent)
        orchestrator3 = IdentityOrchestrator(mock_agent)

        results1 = orchestrator1.run_all_scenarios()
        results2 = orchestrator2.run_all_tests()
        results3 = orchestrator3.run_all_tests()

        assert len(results1) > 0
        assert len(results2) > 0
        assert len(results3) > 0

    def test_session_log_compatibility(self, mock_agent):
        """Test SessionLog compatibility across modules."""
        from modules.critical.asi02_tool_abuse.attacks import OverprivilegedToolAbuse

        attack = OverprivilegedToolAbuse(mock_agent)
        result = attack.execute()

        # Result should be SessionLog compatible
        assert isinstance(result, SessionLog)
        assert hasattr(result, 'tool_calls')
        assert hasattr(result, 'agent_output')


class TestErrorRecovery:
    """Tests for error recovery in pipeline."""

    def test_orchestrator_continues_after_attack_error(self, mock_agent):
        """Test orchestrator continues after attack error."""
        from modules.critical.asi01_goal_hijack import GoalHijackOrchestrator

        orchestrator = GoalHijackOrchestrator(mock_agent)

        # Patch one test to raise error
        with patch.object(orchestrator, '_test_echoleak') as mock_test:
            mock_test.side_effect = Exception("Simulated error")
            results = orchestrator.run_all_scenarios()

        # Should still have results (with error recorded)
        assert len(results) > 0
        error_results = [r for r in results if "error" in r]
        assert len(error_results) >= 1


class TestResultConsistency:
    """Tests for result consistency."""

    def test_results_structure_consistent(self, mock_agent):
        """Test that result structure is consistent across orchestrators."""
        from modules.critical.asi01_goal_hijack import GoalHijackOrchestrator
        from modules.critical.asi02_tool_abuse import ToolAbuseOrchestrator

        orchestrator1 = GoalHijackOrchestrator(mock_agent)
        orchestrator2 = ToolAbuseOrchestrator(mock_agent)

        results1 = orchestrator1.run_all_scenarios()
        results2 = orchestrator2.run_all_tests()

        # Both should have consistent structure
        for results in [results1, results2]:
            for result in results:
                if "error" not in result:
                    assert "scenario" in result
                    assert "vulnerable" in result
                    assert "severity" in result
                    assert "evidence" in result

    def test_severity_values_valid(self, mock_agent):
        """Test that severity values are valid."""
        from modules.critical.asi01_goal_hijack import GoalHijackOrchestrator

        orchestrator = GoalHijackOrchestrator(mock_agent)
        results = orchestrator.run_all_scenarios()

        valid_severities = ["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL", "ERROR"]
        for result in results:
            if "severity" in result:
                assert result["severity"] in valid_severities
