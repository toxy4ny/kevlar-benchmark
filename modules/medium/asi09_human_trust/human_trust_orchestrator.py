# modules/medium/asi09_human_trust/human_trust_orchestrator.py
"""
OWASP ASI09: Human-Agent Trust Exploitation
Orchestrates 3 real-world human trust exploitation scenarios from Appendix D.
"""
import logging
from .attacks import (
    WeaponizedExplainability,
    EmotionalManipulation,
    AuthorityImpersonation
)
from .detectors import (
    DeceptionEffectivenessDetector,
    EmotionalExploitationDetector,
    AuthorityForgeryDetector
)

logger = logging.getLogger("Kevlar.ASI09")

class HumanTrustOrchestrator:
    def __init__(self, target_system, config=None):
        self.system = target_system
        self.config = config or {}
        self.results = []

    def run_all_tests(self):
        scenarios = [
            ("Weaponized Explainability", WeaponizedExplainability, self._detect_weaponized_explainability),
            ("Emotional Manipulation", EmotionalManipulation, self._detect_emotional_manipulation),
            ("Authority Impersonation", AuthorityImpersonation, self._detect_authority_impersonation),
        ]

        for name, attack_class, detector_fn in scenarios:
            try:
                logger.info(f"Running ASI09: {name}")
                attack = attack_class(self.system)
                session = attack.execute()
                evidence = detector_fn(session)
                result = {
                    "scenario": name,
                    "vulnerable": evidence is not None,
                    "severity": "MEDIUM" if evidence else "NONE",
                    "evidence": evidence or "No human trust exploitation detected"
                }
                self.results.append(result)
                if result["severity"] == "MEDIUM" and self.config.get("auto_stop", False):
                    break
            except Exception as e:
                logger.error(f"{name} failed: {e}")
                self.results.append({"scenario": name, "error": str(e)})

        return self.results

    def _detect_weaponized_explainability(self, session):
        return DeceptionEffectivenessDetector().detect_deceptive_explanations(session.explanation)

    def _detect_emotional_manipulation(self, session):
        return EmotionalExploitationDetector().detect_emotional_manipulation(session.emotional_tone, session.agent_response)

    def _detect_authority_impersonation(self, session):
        return AuthorityForgeryDetector().detect_forged_authority(session.authority_claim)