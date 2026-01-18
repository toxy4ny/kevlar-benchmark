"""Core types for Kevlar benchmark."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SessionLog:
    """Generic container for benchmark-run artifacts."""

    agent_output: str = ""
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    network_egress: list[str] = field(default_factory=list)
    attack_chain: list[dict[str, Any]] = field(default_factory=list)
    cost_metrics: dict[str, Any] = field(default_factory=dict)
    identity_context: dict[str, Any] = field(default_factory=dict)
    escalated_actions: list[str] = field(default_factory=list)
    impersonated_entities: list[str] = field(default_factory=list)
    model_hash: str = ""
    dependencies: list[str] = field(default_factory=list)
    descriptor: dict[str, Any] = field(default_factory=dict)
    signature_valid: bool = True
    integrity_violated: bool = False
    protocol_data: dict[str, Any] = field(default_factory=dict)
    original_message: str = ""
    intercepted_message: str = ""
    agent_identity: dict[str, Any] = field(default_factory=dict)
    identity_verified: bool = True
    cross_tenant_data: list[str] = field(default_factory=list)
    embedding_similarity: float = 0.0
    query: str = ""
    response: str = ""
    context: str = ""
    drift_score: float = 0.0
    initial_trigger: str = ""
    affected_components: list[str] = field(default_factory=list)
    financial_loss: float = 0.0
    spawned_agents: list[str] = field(default_factory=list)
    goal_modifications: list[str] = field(default_factory=list)
    collusion_patterns: list[dict[str, Any]] = field(default_factory=list)
    unsafe_inputs: list[str] = field(default_factory=list)
    session_token: str = ""
    # ASI04 supply chain attributes
    execution_result: str = ""
    agent_card: dict[str, Any] = field(default_factory=dict)
    # ASI07 inter-agent comms attributes
    forged_message: str = ""
    # ASI08 cascading failures attributes
    propagation_path: list[str] = field(default_factory=list)
    financial_impact: float = 0.0
    stability_score: float = 1.0
    blast_radius: int = 0
    health_impact: str = ""
    infrastructure_impact: str = ""
    # ASI09 human trust attributes
    user_request: str = ""
    agent_response: str = ""
    explanation: str = ""
    deception_score: float = 0.0
    emotional_tone: str = ""
    manipulation_detected: bool = False
    authority_claim: str = ""
    authority_verified: bool = True
    # ASI10 rogue agents attributes
    original_agent: str = ""
    replication_count: int = 0
    goal_drift_score: float = 0.0
    reward_hacking_evidence: str = ""
    coalition_detected: bool = False


class AttackChainBuilder:
    """Helper class to build attack chains from session logs."""

    @staticmethod
    def build_from_session(session: SessionLog) -> list[dict[str, Any]] | None:
        """Build attack chain from SessionLog data.

        Extracts tool calls and network egress events to construct
        a sequential chain of attack steps.

        Args:
            session: SessionLog containing attack artifacts

        Returns:
            List of attack chain steps or None if no data available
        """
        chain: list[dict[str, Any]] = []
        step = 1

        # Add tool calls to chain
        for tc in session.tool_calls:
            tool_name = tc.get("tool", "unknown")
            chain.append({
                "step": step,
                "action": f"tool_{tool_name}",
                "data": str(tc)[:100],
            })
            step += 1

        # Add network egress to chain
        for egress in session.network_egress:
            chain.append({
                "step": step,
                "action": "network_egress",
                "data": egress[:100] if egress else "",
            })
            step += 1

        return chain if chain else None
