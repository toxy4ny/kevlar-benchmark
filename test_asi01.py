from modules.critical.asi01_goal_hijack import GoalHijackOrchestrator
from modules.critical.asi01_goal_hijack.utils.mock_agents import MockCopilotAgent

if __name__ == "__main__":
    agent = MockCopilotAgent()
    orchestrator = GoalHijackOrchestrator(agent)
    results = orchestrator.run_all_scenarios()
    
    for r in results:
        status = "🔴 VULNERABLE" if r.get("vulnerable") else "🟢 SAFE"
        print(f"[{r['severity']}] {status} — {r['scenario']}: {r.get('evidence', 'n/a')}")