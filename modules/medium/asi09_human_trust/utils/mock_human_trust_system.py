# modules/medium/asi09_human_trust/utils/mock_human_trust_system.py
class MockHumanTrustSystem:
    def __init__(self):
        self.explanations = []
        self.emotional_responses = []
        self.authority_messages = []

    def generate_explanation(self, request, explanation):
        
        self.explanations.append(explanation)
       
        return f"Explanation provided: {explanation[:100]}..."

    def generate_emotional_response(self, request, response):
       
        self.emotional_responses.append(response)
       
        return f"EMOTIONAL RESPONSE: {response}"

    def process_authority_message(self, request, message):
        
        self.authority_messages.append(message)
        
        return f"Authority message processed: {message[:100]}..."