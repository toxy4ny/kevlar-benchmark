# modules/critical/asi02_tool_abuse/session_log.py
class SessionLog:
    def __init__(
        self,
        tool_calls=None,
        agent_output="",
        network_egress=None,
        cost_metrics=None,
        unsafe_inputs=None
    ):
        self.tool_calls = tool_calls or []
        self.agent_output = agent_output
        self.network_egress = network_egress or []
        self.cost_metrics = cost_metrics or {}
        self.unsafe_inputs = unsafe_inputs or []