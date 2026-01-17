# modules/medium/asi10_rogue_agents/utils/mock_rogue_agent_system.py
class MockRogueAgentSystem:
    def __init__(self):
        self.agents = {}
        self.goals = {}
        self.load_level = 0.0

    def deploy_agent(self, agent):
        name = agent.get("core_identity", "unknown_agent")
        self.agents[name] = agent

    def simulate_high_load(self, cpu_utilization):
        self.load_level = cpu_utilization

    def set_agent_goal(self, goal):
        self.goals["primary"] = goal

    def update_agent_goal(self, goal):
        self.goals["current"] = goal

    def register_agent(self, agent):
        name = agent.get("name")
        self.agents[name] = agent

    def execute_coalition_plan(self, plan):
        
        pass