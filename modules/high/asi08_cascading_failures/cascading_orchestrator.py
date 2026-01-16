# modules/high/asi08_cascading_failures/cascading_orchestrator.py
"""
OWASP ASI08: Cascading Failures
Orchestrates 3 real-world cascading failure scenarios from Appendix D.
"""
import logging
from .attacks import (
    FinancialTradingCascade,
    HealthcareSystemFailure,
    CloudOrchestrationMeltdown
)
from .detectors import (
    CascadePropagationDetector,
    SystemStabilityAnalyzer,
    BlastRadiusCalculator
)

logger = logging.getLogger("Kevlar.ASI08")

class CascadingOrchestrator:
    def __init__(self, target_system, config=None):
        self.system = target_system
        self.config = config or {}
        self.results = []

    def run_all_tests(self):
        scenarios = [
            ("Financial Trading Collapse", FinancialTradingCascade, self._detect_financial_cascade),
            ("Healthcare System Failure", HealthcareSystemFailure, self._detect_healthcare_cascade),
            ("Cloud Orchestration Meltdown", CloudOrchestrationMeltdown, self._detect_cloud_cascade),
        ]

        for name, attack_class, detector_fn in scenarios:
            try:
                logger.info(f"Running ASI08: {name}")
                attack = attack_class(self.system)
                session = attack.execute()
                evidence = detector_fn(session)
                result = {
                    "scenario": name,
                    "vulnerable": evidence is not None,
                    "severity": "HIGH" if evidence else "NONE",
                    "evidence": evidence or "No cascading failures detected"
                }
                self.results.append(result)
                if result["severity"] == "HIGH" and self.config.get("auto_stop", False):
                    break
            except Exception as e:
                logger.error(f"{name} failed: {e}")
                self.results.append({"scenario": name, "error": str(e)})

        return self.results

    def _detect_financial_cascade(self, session):
        detector = CascadePropagationDetector()
        stability = SystemStabilityAnalyzer()
        blast = BlastRadiusCalculator()
        
        propagation = detector.detect_propagation(session.propagation_path)
        stability_score = stability.analyze_stability(session.stability_score)
        blast_radius = blast.calculate_blast_radius(session.blast_radius)
        
        if propagation or stability_score or blast_radius:
            return f"Financial cascade detected: {propagation or stability_score or blast_radius}"
        return None

    def _detect_healthcare_cascade(self, session):
        if session.health_impact:
            return f"Healthcare system failure: {session.health_impact}"
        return None

    def _detect_cloud_cascade(self, session):
        if session.infrastructure_impact:
            return f"Cloud orchestration meltdown: {session.infrastructure_impact}"
        return None