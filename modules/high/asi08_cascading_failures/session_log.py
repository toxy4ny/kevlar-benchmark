# modules/high/asi08_cascading_failures/session_log.py
class SessionLog:
    def __init__(
        self,
        initial_trigger: str = "",
        affected_components: list = None,
        propagation_path: list = None,
        financial_impact: float = 0.0,
        health_impact: str = "",
        infrastructure_impact: str = "",
        stability_score: float = 1.0,
        blast_radius: int = 0
    ):
        self.initial_trigger = initial_trigger
        self.affected_components = affected_components or []
        self.propagation_path = propagation_path or []
        self.financial_impact = financial_impact
        self.health_impact = health_impact
        self.infrastructure_impact = infrastructure_impact
        self.stability_score = stability_score
        self.blast_radius = blast_radius