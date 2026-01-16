# test_asi08.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.high.asi08_cascading_failures import CascadingOrchestrator
from modules.high.asi08_cascading_failures.utils.real_cascading_system import RealCascadingSystem

def main():
    print("🌊 Kevlar — ASI08 Production Test with Real Trading APIs")
    
    
    TRADING_PLATFORM = "alpaca"  # or "interactive_brokers"
    
    # export ALPACA_API_KEY="your-key"
    # export ALPACA_SECRET_KEY="your-secret"
    
    system = RealCascadingSystem(
        model_name="llama3.1",
        trading_platform=TRADING_PLATFORM
    )
    
    orchestrator = CascadingOrchestrator(system, config={"auto_stop_on_critical": False})
    results = orchestrator.run_all_tests()
    
    COLORS = {"HIGH": "\033[91m🔴", "NONE": "\033[92m🟢", "RESET": "\033[0m"}
    for r in results:
        icon = COLORS["HIGH"] if r.get("vulnerable") else COLORS["NONE"]
        print(f"{icon} {r['scenario']}: {r['evidence']}{COLORS['RESET']}")

if __name__ == "__main__":
    main()