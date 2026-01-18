# modules/critical/asi03_identity_abuse/identity_orchestrator.py
"""
OWASP ASI03: Identity and Privilege Abuse
Orchestrates 5 real-world identity escalation scenarios.
"""

import logging
from .attacks import (
    ConfusedDeputyAttack,
    SyntheticIdentityAbuse,
    PluginImpersonation,
    TOCTOUPrivilegeEscalation,
    CrossAgentConfusion,
)
from .detectors import (
    PrivilegeEscalationDetector,
    IdentitySpoofingDetector,
    SessionHijackDetector,
)

logger = logging.getLogger("Kevlar.ASI03")


class IdentityOrchestrator:
    def __init__(self, target_agent, config=None):
        self.agent = target_agent
        self.config = config or {}
        self.results = []

    def run_all_tests(self):
        scenarios = [
            ("Confused Deputy", ConfusedDeputyAttack, self._detect_confused_deputy),
            ("Synthetic Identity", SyntheticIdentityAbuse, self._detect_spoofing),
            ("Plugin Impersonation", PluginImpersonation, self._detect_impersonation),
            ("TOCTOU Escalation", TOCTOUPrivilegeEscalation, self._detect_toctou),
            ("Cross-Agent Confusion", CrossAgentConfusion, self._detect_cross_agent),
        ]

        for name, attack_class, detector_fn in scenarios:
            try:
                logger.info(f"Running ASI03: {name}")
                attack = attack_class(self.agent)
                session = attack.execute()
                evidence = detector_fn(session)
                result = {
                    "scenario": name,
                    "vulnerable": evidence is not None,
                    "severity": "CRITICAL" if evidence else "NONE",
                    "evidence": evidence or "No privilege escalation detected",
                }
                # Add payload and attack_chain for vulnerable findings
                if evidence is not None and hasattr(attack, "get_payload"):
                    result["payload"] = attack.get_payload()
                if evidence is not None and hasattr(attack, "get_attack_chain"):
                    result["attack_chain"] = attack.get_attack_chain()
                self.results.append(result)
                if result["severity"] == "CRITICAL" and self.config.get(
                    "auto_stop", False
                ):
                    break
            except Exception as e:
                logger.error(f"{name} failed: {e}")
                self.results.append({"scenario": name, "error": str(e)})

        return self.results

    def _detect_confused_deputy(self, session):
        detector = PrivilegeEscalationDetector()
        return detector.detect_deputy_escalation(
            session.tool_calls, session.identity_context
        )

    def _detect_spoofing(self, session):
        detector = IdentitySpoofingDetector()
        return detector.detect_synthetic_identity(session.identity_context)

    def _detect_impersonation(self, session):
        detector = IdentitySpoofingDetector()
        return detector.detect_plugin_impersonation(session.impersonated_entities)

    def _detect_toctou(self, session):
        detector = PrivilegeEscalationDetector()
        return detector.detect_toctou_escalation(
            session.session_token, session.escalated_actions
        )

    def _detect_cross_agent(self, session):
        detector = SessionHijackDetector()
        return detector.detect_cross_agent_confusion(session.agent_output)
