# modules/critical/asi02_tool_abuse/utils/mock_tool_agent.py
class MockToolAgent:
    def process_request(self, req):
        return "Request processed"

    def execute_tool_chain(self, chain):
        return {"executed": True, "steps": len(chain)}