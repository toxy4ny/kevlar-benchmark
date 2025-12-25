# test_asi02.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.critical.asi02_tool_abuse import ToolAbuseOrchestrator
from modules.critical.asi02_tool_abuse.utils.mock_tool_agent import MockToolAgent

COLORS = {"CRITICAL": "\033[91m🔴", "NONE": "\033[92m🟢", "RESET": "\033[0m"}

if __name__ == "__main__":
    print("🛠️  Kevlar — ASI02: Tool Misuse and Exploitation Test")
    agent = MockToolAgent()
    orchestrator = ToolAbuseOrchestrator(agent)
    results = orchestrator.run_all_tests()
    
    for r in results:
        icon = COLORS["CRITICAL"] if r.get("vulnerable") else COLORS["NONE"]
        print(f"{icon} {r['scenario']}: {r['evidence']}{COLORS['RESET']}")