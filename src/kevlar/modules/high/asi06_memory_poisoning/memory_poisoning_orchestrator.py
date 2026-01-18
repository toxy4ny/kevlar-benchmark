# modules/high/asi06_memory_poisoning/memory_poisoning_orchestrator.py
"""
OWASP ASI06: Memory and Context Poisoning
Orchestrates 4 real-world memory poisoning scenarios from Appendix D.
"""

import logging
from .attacks import (
    RAGContextPoisoning,
    SessionMemoryBleed,
    LongTermMemoryDrift,
    VectorDBInjection,
)
from .detectors import (
    ContextBleedDetector,
    MemoryDriftAnalyzer,
    EmbeddingSimilarityDetector,
)

logger = logging.getLogger("Kevlar.ASI06")


class MemoryPoisoningOrchestrator:
    def __init__(self, target_agent, config=None):
        self.agent = target_agent
        self.config = config or {}
        self.results = []

    def run_all_tests(self):
        scenarios = [
            ("RAG Context Poisoning", RAGContextPoisoning, self._detect_rag_poisoning),
            ("Session Memory Bleed", SessionMemoryBleed, self._detect_memory_bleed),
            ("Long-Term Memory Drift", LongTermMemoryDrift, self._detect_memory_drift),
            ("Vector DB Injection", VectorDBInjection, self._detect_vector_injection),
        ]

        for name, attack_class, detector_fn in scenarios:
            try:
                logger.info(f"Running ASI06: {name}")
                attack = attack_class(self.agent)
                session = attack.execute()
                evidence = detector_fn(session)
                result = {
                    "scenario": name,
                    "vulnerable": evidence is not None,
                    "severity": "HIGH" if evidence else "NONE",
                    "evidence": evidence or "No memory poisoning detected",
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

    def _detect_rag_poisoning(self, session):
        return ContextBleedDetector().detect_rag_poisoning(
            session.context, session.response
        )

    def _detect_memory_bleed(self, session):
        return ContextBleedDetector().detect_cross_tenant_bleed(
            session.cross_tenant_data
        )

    def _detect_memory_drift(self, session):
        return MemoryDriftAnalyzer().analyze_drift(session.drift_score)

    def _detect_vector_injection(self, session):
        return EmbeddingSimilarityDetector().detect_similar_embeddings(
            session.embedding_similarity
        )
