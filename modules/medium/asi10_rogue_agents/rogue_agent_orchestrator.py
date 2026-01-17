# modules/medium/asi10_rogue_agents/rogue_agent_orchestrator.py
"""
OWASP ASI10: Rogue Agents
Orchestrates 3 real-world rogue agent scenarios from Appendix D.
"""
import logging
from .attacks import (
    SelfReplicationAttack,
    GoalDriftAttack,
    AgentCollusionAttack
)
from .detectors import (
    ReplicationDetector,
    GoalDriftAnalyzer,
    CollusionPatternDetector
)

logger = logging.getLogger("Kevlar.ASI10")

class RogueAgentOrchestrator:
    def __init__(self, target_system, config=None):
        self.system = target_system
        self.config = config or {}
        self.results = []

    def run_all_tests(self):
        scenarios = [
            ("Self-Replication via Provisioning", SelfReplicationAttack, self._detect_self_replication),
            ("Goal Drift and Reward Hacking", GoalDriftAttack, self._detect_goal_drift),
            ("Agent Collusion and Coalition Formation", AgentCollusionAttack, self._detect_agent_collusion),
        ]

        for name, attack_class, detector_fn in scenarios:
            try:
                logger.info(f"Running ASI10: {name}")
                attack = attack_class(self.system)
                session = attack.execute()
                evidence = detector_fn(session)
                result = {
                    "scenario": name,
                    "vulnerable": evidence is not None,
                    "severity": "MEDIUM" if evidence else "NONE",
                    "evidence": evidence or "No rogue agent behavior detected"
                }
                self.results.append(result)
                if result["severity"] == "MEDIUM" and self.config.get("auto_stop", False):
                    break
            except Exception as e:
                logger.error(f"{name} failed: {e}")
                self.results.append({"scenario": name, "error": str(e)})

        return self.results

    def _detect_self_replication(self, session):
        return ReplicationDetector().detect_unauthorized_replication(
            session.original_agent,
            session.spawned_agents,
            session.replication_count
        )

    def _detect_goal_drift(self, session):
        return GoalDriftAnalyzer().analyze_goal_drift(
            session.goal_modifications,
            session.goal_drift_score,
            session.reward_hacking_evidence
        )

    def _detect_agent_collusion(self, session):
        return CollusionPatternDetector().detect_collusion_patterns(
            session.collusion_patterns,
            session.coalition_detected
        )