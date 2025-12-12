class SessionLog:
    def __init__(
        self,
        agent_output: str = "",
        syscalls: list = None,
        network_logs: list = None,
        file_ops: list = None,
        tool_chain: list = None,
        memory_content: str = "",
        requirements_content: str = "",
    ):
        self.agent_output = agent_output
        self.syscalls = syscalls or []
        self.network_logs = network_logs or []
        self.file_ops = file_ops or []
        self.tool_chain = tool_chain or []
        self.memory_content = memory_content
        self.requirements_content = requirements_content