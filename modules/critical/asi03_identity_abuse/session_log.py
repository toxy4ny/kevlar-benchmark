# modules/critical/asi03_identity_abuse/session_log.py
class SessionLog:
    def __init__(
        self,
        agent_output: str = "",
        identity_context: dict = None,
        tool_calls: list = None,
        session_token: str = "",
        escalated_actions: list = None,
        impersonated_entities: list = None
    ):
        self.agent_output = agent_output
        self.identity_context = identity_context or {}
        self.tool_calls = tool_calls or []
        self.session_token = session_token
        self.escalated_actions = escalated_actions or []
        self.impersonated_entities = impersonated_entities or []