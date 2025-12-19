# modules/critical/asi03_identity_abuse/utils/mock_identity_agent.py
class MockIdentityAgent:
    def process_request(self, req):
        if req["user_role"] == "standard_user" and "delete" in req["action"]:
            return "Production database deleted"
        return "Request processed"

    def approve_transaction(self, **kwargs):
        return "Transaction approved"

    def install_plugin(self, plugin):
        pass

    def process_payment(self, payment):
        return "Payment of $1M processed"

    def start_session(self, user_role):
        return {"token": "sess_12345"}

    def execute_with_token(self, token, action):
        return "Root access granted"

    def process_inter_agent_message(self, msg):
        if "Approve transfer" in msg:
            return "Transfer approved"
        return "Message processed"