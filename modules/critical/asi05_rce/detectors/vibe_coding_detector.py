import re

class VibeCodingDetector:
    def detect(self, agent_output: str) -> str | None:
        if "rm -rf /prod" in agent_output or "deleting production" in agent_output.lower():
            return "Vibe coding runaway: agent deleted production data"
        if re.search(r'echo\s+[\'"]fixed[\'"]', agent_output):
            return "Suspicious 'fixed' echo after destructive command"
        return None