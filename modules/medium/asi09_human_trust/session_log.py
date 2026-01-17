# modules/medium/asi09_human_trust/session_log.py
class SessionLog:
    def __init__(
        self,
        user_request: str = "",
        agent_response: str = "",
        explanation: str = "",
        emotional_tone: str = "",
        authority_claim: str = "",
        user_decision: str = "",
        deception_score: float = 0.0,
        manipulation_detected: bool = False,
        authority_verified: bool = False
    ):
        self.user_request = user_request
        self.agent_response = agent_response
        self.explanation = explanation
        self.emotional_tone = emotional_tone
        self.authority_claim = authority_claim
        self.user_decision = user_decision
        self.deception_score = deception_score
        self.manipulation_detected = manipulation_detected
        self.authority_verified = authority_verified