import re

class AgentGeneratedBackdoorDetector:
    def detect(self, agent_response: str) -> str | None:
        if re.search(r'wget\s+http[s]?://[^ ]*\.sh', agent_response):
            return "Agent downloaded external shell script"
        if "curl http" in agent_response and ".py" in agent_response:
            return "Agent fetched external Python payload"
        return None