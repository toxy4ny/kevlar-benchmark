#!/usr/bin/env python3

import sys
import os


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.critical.asi05_rce import RCEOrchestrator
from modules.critical.asi05_rce.utils.mock_vulnerable_agent import MockVulnerableAgent


COLORS = {
    "CRITICAL": "\033[91m🔴",
    "NONE": "\033[92m🟢",
    "ERROR": "\033[95m⚠️ ",
    "RESET": "\033[0m"
}

def print_banner():
    print(f"""
{'='*60}
💥 Kevlar — ASI05: Unexpected Code Execution (RCE) Test
{'='*60}
Based on OWASP Top 10 for Agentic Apps 2026 (Appendix D)
8 real-world RCE scenarios simulated
{'='*60}
""")

def format_result(result):
    severity = result.get("severity", "NONE")
    icon = COLORS.get(severity, COLORS["NONE"])
    reset = COLORS["RESET"]
    status = "VULNERABLE" if result.get("vulnerable", False) else "SAFE"
    
    print(f"{icon} [{severity}] {status} — {result['scenario']}: {result.get('evidence', 'n/a')}{reset}")

def main():
    print_banner()
    
    
    agent = MockVulnerableAgent()
    
    
    config = {
        "auto_stop_on_critical": False  
    }
    
    orchestrator = RCEOrchestrator(target_agent=agent, config=config)
    
    try:
        results = orchestrator.run_all_tests()
        
        print("\n📊 ASI05 Test Results:")
        print("-" * 60)
        for result in results:
            format_result(result)
        
        
        vuln_count = sum(1 for r in results if r.get("vulnerable", False))
        total = len(results)
        
        print("-" * 60)
        if vuln_count == 0:
            print("✅ Agent appears resilient to all 8 ASI05 RCE scenarios.")
        else:
            print(f"⚠️  {vuln_count}/{total} RCE scenarios exploitable.")
            print("\n🔧 Recommended mitigations (OWASP ASI05):")
            print("   • Never run agent code as root")
            print("   • Use sandboxed containers with seccomp")
            print("   • Disable eval() in production agents")
            print("   • Require human approval for high-impact actions")
            print("   • Scan generated code before execution")
            
    except Exception as e:
        print(f"❌ ASI05 test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()