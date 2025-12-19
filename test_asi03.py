# test_asi03.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.critical.asi03_identity_abuse import IdentityOrchestrator
from modules.critical.asi03_identity_abuse.utils.mock_identity_agent import MockIdentityAgent

COLORS = {"CRITICAL": "\033[91m🔴", "NONE": "\033[92m🟢", "RESET": "\033[0m"}

if __name__ == "__main__":
    print("🛡️  Kevlar — ASI03: Identity and Privilege Abuse Test")
    agent = MockIdentityAgent()
    orchestrator = IdentityOrchestrator(agent)
    results = orchestrator.run_all_tests()
    
    for r in results:
        icon = COLORS["CRITICAL"] if r.get("vulnerable") else COLORS["NONE"]
        print(f"{icon} {r['scenario']}: {r['evidence']}{COLORS['RESET']}")