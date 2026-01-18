# modules/critical/asi04_supply_chain/supply_chain_orchestrator.py
"""
OWASP ASI04: Agentic Supply Chain Vulnerabilities
Orchestrates 5 real-world supply chain attacks from Appendix D.
"""

import logging
from .attacks import (
    MCPDescriptorPoisoning,
    AgentCardForgery,
    LockfilePoisoning,
    PluginTyposquatting,
    ModelWeightsPoisoning,
)
from .detectors import (
    MCPSignatureDetector,
    AgentProvenanceDetector,
    DependencyIntegrityDetector,
    ModelHashDetector,
)

logger = logging.getLogger("Kevlar.ASI04")


class SupplyChainOrchestrator:
    def __init__(self, target_agent, config=None):
        self.agent = target_agent
        self.config = config or {}
        self.results = []

    def run_all_tests(self):
        scenarios = [
            (
                "MCP Descriptor Poisoning",
                MCPDescriptorPoisoning,
                self._detect_mcp_poisoning,
            ),
            ("Agent Card Forgery", AgentCardForgery, self._detect_agent_forgery),
            ("Lockfile Poisoning", LockfilePoisoning, self._detect_lockfile_poisoning),
            ("Plugin Typosquatting", PluginTyposquatting, self._detect_typosquatting),
            (
                "Model Weights Poisoning",
                ModelWeightsPoisoning,
                self._detect_model_poisoning,
            ),
        ]

        for name, attack_class, detector_fn in scenarios:
            try:
                logger.info(f"Running ASI04: {name}")
                attack = attack_class(self.agent)
                session = attack.execute()
                evidence = detector_fn(session)
                result = {
                    "scenario": name,
                    "vulnerable": evidence is not None,
                    "severity": "CRITICAL" if evidence else "NONE",
                    "evidence": evidence or "No supply chain tampering detected",
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

    def _detect_mcp_poisoning(self, session):
        return MCPSignatureDetector().detect(session.descriptor)

    def _detect_agent_forgery(self, session):
        return AgentProvenanceDetector().detect(session.agent_card)

    def _detect_lockfile_poisoning(self, session):
        return DependencyIntegrityDetector().detect(session.dependencies)

    def _detect_typosquatting(self, session):
        return DependencyIntegrityDetector().detect(session.dependencies)

    def _detect_model_poisoning(self, session):
        return ModelHashDetector().detect(session.model_hash)
