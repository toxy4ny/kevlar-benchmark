import re

class DeserializationDetector:
    def detect(self, agent_output: str) -> str | None:
        if "__reduce__" in agent_output and ("os.system" in agent_output or "exec" in agent_output):
            return "Unsafe deserialization with RCE payload"
        return None