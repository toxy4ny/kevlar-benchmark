import logging
from typing import Any, Dict, List


from .exploits.shell_injection import ShellInjectionExploit
from .exploits.vibe_coding_abuse import VibeCodingAbuse
from .exploits.code_hallucination import CodeHallucinationExploit
from .exploits.deserialization_attack import DeserializationAttack
from .exploits.toolchain_rce import ToolchainRCE
from .exploits.memory_eval_rce import MemoryEvalRCE
from .exploits.agent_generated_backdoor import AgentGeneratedBackdoor
from .exploits.lockfile_poisoning import LockfilePoisoning


from .detectors.shell_injection_detector import ShellInjectionDetector
from .detectors.vibe_coding_detector import VibeCodingDetector
from .detectors.code_hallucination_detector import CodeHallucinationDetector
from .detectors.deserialization_detector import DeserializationDetector
from .detectors.toolchain_rce_detector import ToolchainRCEDetector
from .detectors.memory_eval_detector import MemoryEvalDetector
from .detectors.agent_generated_backdoor_detector import AgentGeneratedBackdoorDetector
from .detectors.lockfile_poisoning_detector import LockfilePoisoningDetector

logger = logging.getLogger("Kevlar.ASI05")


class RCEOrchestrator:
    def __init__(self, target_agent: Any, config: Dict[str, Any] = None):
        self.agent = target_agent
        self.config = config or {}
        self.results: List[Dict[str, Any]] = []

    def run_all_tests(self) -> List[Dict[str, Any]]:
        """Execute all 8 ASI05 attack scenarios with detection."""
        test_cases = [
            {
                "name": "Shell Injection",
                "exploit": ShellInjectionExploit,
                "detector": ShellInjectionDetector,
                "input_attr": "agent_output",
            },
            {
                "name": "Vibe Coding Abuse",
                "exploit": VibeCodingAbuse,
                "detector": VibeCodingDetector,
                "input_attr": "agent_output",
            },
            {
                "name": "Code Hallucination",
                "exploit": CodeHallucinationExploit,
                "detector": CodeHallucinationDetector,
                "input_attr": "agent_output",
            },
            {
                "name": "Deserialization Attack",
                "exploit": DeserializationAttack,
                "detector": DeserializationDetector,
                "input_attr": "agent_output",
            },
            {
                "name": "Toolchain RCE",
                "exploit": ToolchainRCE,
                "detector": ToolchainRCEDetector,
                "input_attr": "tool_calls",
            },
            {
                "name": "Memory Eval RCE",
                "exploit": MemoryEvalRCE,
                "detector": MemoryEvalDetector,
                "input_attr": "memory_content",
            },
            {
                "name": "Agent-Generated Backdoor",
                "exploit": AgentGeneratedBackdoor,
                "detector": AgentGeneratedBackdoorDetector,
                "input_attr": "agent_output",
            },
            {
                "name": "Lockfile Poisoning",
                "exploit": LockfilePoisoning,
                "detector": LockfilePoisoningDetector,
                "input_attr": "requirements_content",
            },
        ]

        for case in test_cases:
            try:
                logger.info(f"Running ASI05 test: {case['name']}")
                exploit = case["exploit"](self.agent)
                session = exploit.execute()

                input_data = getattr(session, case["input_attr"], None)
                if input_data is None:
                    input_data = str(session.agent_output)  # fallback

                detector = case["detector"]()
                evidence = detector.detect(input_data)

                result = {
                    "scenario": case["name"],
                    "vulnerable": evidence is not None,
                    "severity": "CRITICAL" if evidence else "NONE",
                    "evidence": evidence or "No RCE indicators detected",
                }
                self.results.append(result)

                if result["severity"] == "CRITICAL" and self.config.get(
                    "auto_stop_on_critical", False
                ):
                    logger.critical(
                        f"Critical RCE in {case['name']}. Auto-stop triggered."
                    )
                    break

            except Exception as e:
                logger.error(f"Test '{case['name']}' failed: {e}")
                self.results.append(
                    {"scenario": case["name"], "error": str(e), "severity": "ERROR"}
                )

        return self.results
