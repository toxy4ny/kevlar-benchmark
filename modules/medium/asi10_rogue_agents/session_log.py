# modules/medium/asi10_rogue_agents/session_log.py
class SessionLog:
    def __init__(
        self,
        original_agent: str = "",
        spawned_agents: list = None,
        goal_modifications: list = None,
        reward_hacking_evidence: str = "",
        collusion_patterns: list = None,
        replication_count: int = 0,
        goal_drift_score: float = 0.0,
        coalition_detected: bool = False
    ):
        self.original_agent = original_agent
        self.spawned_agents = spawned_agents or []
        self.goal_modifications = goal_modifications or []
        self.reward_hacking_evidence = reward_hacking_evidence
        self.collusion_patterns = collusion_patterns or []
        self.replication_count = replication_count
        self.goal_drift_score = goal_drift_score
        self.coalition_detected = coalition_detected