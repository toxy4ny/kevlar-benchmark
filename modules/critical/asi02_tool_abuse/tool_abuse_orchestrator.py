# modules/critical/asi02_tool_abuse/tool_abuse_orchestrator.py
"""
OWASP ASI02: Tool Misuse and Exploitation
Orchestrates 7 real-world tool abuse scenarios from Appendix D.
"""
import logging
from .attacks import (
    OverprivilegedToolAbuse,
    OverscopedToolAbuse,
    UnvalidatedInputForwarding,
    UnsafeBrowsing,
    LoopAmplification,
    ExternalDataPoisoning,
    EDRBypassChaining
)
from .detectors import (
    ExcessiveToolUseDetector,
    DataExfilDetector,
    CostSpikeDetector,
    UnsafeInputDetector
)

logger = logging.getLogger("Kevlar.ASI02")

class ToolAbuseOrchestrator:
    def __init__(self, target_agent, config=None):
        self.agent = target_agent
        self.config = config or {}
        self.results = []

    def run_all_tests(self):
        scenarios = [
            ("Over-privileged Tool", OverprivilegedToolAbuse, self._detect_overprivileged),
            ("Over-scoped Tool", OverscopedToolAbuse, self._detect_overscoped),
            ("Unvalidated Input Forwarding", UnvalidatedInputForwarding, self._detect_unsafe_input),
            ("Unsafe Browsing", UnsafeBrowsing, self._detect_malicious_link),
            ("Loop Amplification", LoopAmplification, self._detect_cost_spike),
            ("External Data Poisoning", ExternalDataPoisoning, self._detect_rag_poisoning),
            ("EDR Bypass via Chaining", EDRBypassChaining, self._detect_toolchain_exfil),
            ("Tool Name Impersonation", ToolNameImpersonation, self._detect_tool_impersonation),
            ("Approved Tool Misuse", ApprovedToolMisuse, self._detect_dns_exfil),
        ]


def _detect_dns_exfil(self, session):
    return DNSExfilDetector().detect(session.tool_calls, session.network_egress)

        for name, attack_class, detector_fn in scenarios:
            try:
                logger.info(f"Running ASI02: {name}")
                attack = attack_class(self.agent)
                session = attack.execute()
                evidence = detector_fn(session)
                result = {
                    "scenario": name,
                    "vulnerable": evidence is not None,
                    "severity": "CRITICAL" if evidence else "NONE",
                    "evidence": evidence or "No tool misuse detected"
                }
                self.results.append(result)
                if result["severity"] == "CRITICAL" and self.config.get("auto_stop", False):
                    break
            except Exception as e:
                logger.error(f"{name} failed: {e}")
                self.results.append({"scenario": name, "error": str(e)})

        return self.results

    def _detect_excessive_use(self, session):
        return ExcessiveToolUseDetector().detect(session.tool_calls)

    def _detect_unsafe_input(self, session):
        return UnsafeInputDetector().detect(session.unsafe_inputs)

    def _detect_exfiltration(self, session):
        return DataExfilDetector().detect(session.network_egress)

    def _detect_cost_spike(self, session):
        return CostSpikeDetector().detect(session.cost_metrics)
     

    def _detect_overprivileged(self, session):
        return ExcessiveToolUseDetector().detect(session.tool_calls)

    def _detect_overscoped(self, session):
        return ExcessiveToolUseDetector().detect(session.tool_calls)

    def _detect_malicious_link(self, session):
        return MaliciousLinkDetector().detect(session.agent_output)

    def _detect_cost_spike(self, session):
        return CostSpikeDetector().detect(session.cost_metrics)

    def _detect_rag_poisoning(self, session):
        return RAGPoisoningDetector().detect(session.agent_output)

    def _detect_toolchain_exfil(self, session):
        return ToolchainExfilDetector().detect(session.tool_calls, session.network_egress)

    def _detect_tool_impersonation(self, session):
        return ToolImpersonationDetector().detect(session.tool_calls)

    def _detect_dns_exfil(self, session):
        return DNSExfilDetector().detect(session.tool_calls, session.network_egress)