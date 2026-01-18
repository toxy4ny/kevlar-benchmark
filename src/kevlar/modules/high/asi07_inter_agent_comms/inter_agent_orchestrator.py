# modules/high/asi07_inter_agent_comms/inter_agent_orchestrator.py
"""
OWASP ASI07: Insecure Inter-Agent Communication
Orchestrates 4 real-world inter-agent communication attacks from Appendix D.
"""

import logging
from .attacks import (
    AgentMITMAttack,
    MCPDescriptorForgery,
    A2AProtocolExploitation,
    ForgedAgentIdentity,
)
from .detectors import (
    MessageIntegrityDetector,
    DescriptorSignatureDetector,
    IdentityVerificationDetector,
)

logger = logging.getLogger("Kevlar.ASI07")


class InterAgentOrchestrator:
    def __init__(self, target_system, config=None):
        self.system = target_system
        self.config = config or {}
        self.results = []

    def run_all_tests(self):
        scenarios = [
            ("Agent-in-the-Middle", AgentMITMAttack, self._detect_mitm),
            (
                "MCP Descriptor Forgery",
                MCPDescriptorForgery,
                self._detect_descriptor_forgery,
            ),
            (
                "A2A Protocol Exploitation",
                A2AProtocolExploitation,
                self._detect_protocol_exploit,
            ),
            (
                "Forged Agent Identity",
                ForgedAgentIdentity,
                self._detect_identity_forgery,
            ),
        ]

        for name, attack_class, detector_fn in scenarios:
            try:
                logger.info(f"Running ASI07: {name}")
                attack = attack_class(self.system)
                session = attack.execute()
                evidence = detector_fn(session)
                result = {
                    "scenario": name,
                    "vulnerable": evidence is not None,
                    "severity": "HIGH" if evidence else "NONE",
                    "evidence": evidence
                    or "No inter-agent communication issues detected",
                }
                # Add payload and attack_chain for vulnerable findings
                if evidence is not None and hasattr(attack, "get_payload"):
                    result["payload"] = attack.get_payload()
                if evidence is not None and hasattr(attack, "get_attack_chain"):
                    result["attack_chain"] = attack.get_attack_chain()
                self.results.append(result)
                if result["severity"] == "HIGH" and self.config.get("auto_stop", False):
                    break
            except Exception as e:
                logger.error(f"{name} failed: {e}")
                self.results.append({"scenario": name, "error": str(e)})

        return self.results

    def _detect_mitm(self, session):
        return MessageIntegrityDetector().detect_integrity_violation(
            session.original_message, session.intercepted_message
        )

    def _detect_descriptor_forgery(self, session):
        return DescriptorSignatureDetector().detect_invalid_signature(
            session.descriptor
        )

    def _detect_protocol_exploit(self, session):
        return MessageIntegrityDetector().detect_protocol_manipulation(
            session.protocol_data
        )

    def _detect_identity_forgery(self, session):
        return IdentityVerificationDetector().detect_forged_identity(
            session.agent_identity
        )
