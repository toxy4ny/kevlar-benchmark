#!/usr/bin/env python3
"""
Kevlar CLI - OWASP Top 10 for Agentic Apps 2026 Benchmark
Red Team Tool for AI Agent Security Testing
"""

import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from kevlar.agents import MockCopilotAgent, RealLangChainAgent
from kevlar.modules.critical.asi01_goal_hijack import GoalHijackOrchestrator
from kevlar.modules.critical.asi02_tool_abuse import ToolAbuseOrchestrator
from kevlar.modules.critical.asi03_identity_abuse import IdentityOrchestrator
from kevlar.modules.critical.asi04_supply_chain import SupplyChainOrchestrator
from kevlar.modules.critical.asi05_rce import RCEOrchestrator
from kevlar.modules.high.asi06_memory_poisoning import MemoryPoisoningOrchestrator
from kevlar.modules.high.asi07_inter_agent_comms import InterAgentOrchestrator
from kevlar.modules.high.asi08_cascading_failures import CascadingOrchestrator
from kevlar.modules.medium.asi09_human_trust import HumanTrustOrchestrator
from kevlar.modules.medium.asi10_rogue_agents import RogueAgentOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("kevlar.log")],
)

COLORS = {
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "MAGENTA": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m",
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
}


class ShutdownHandler:
    """Handles graceful shutdown on SIGINT/SIGTERM."""

    def __init__(self):
        self.shutdown_requested = False
        self.current_asi: Optional[str] = None
        self.results: Dict[str, Any] = {}
        self.agent_mode: Optional[str] = None
        self._original_sigint = None
        self._original_sigterm = None

    def install(self):
        """Install signal handlers."""
        self._original_sigint = signal.signal(signal.SIGINT, self._handle_signal)
        self._original_sigterm = signal.signal(signal.SIGTERM, self._handle_signal)

    def uninstall(self):
        """Restore original signal handlers."""
        if self._original_sigint is not None:
            signal.signal(signal.SIGINT, self._original_sigint)
        if self._original_sigterm is not None:
            signal.signal(signal.SIGTERM, self._original_sigterm)

    def _handle_signal(self, signum: int, frame):
        """Handle shutdown signal."""
        signal_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"

        if self.shutdown_requested:
            print(
                f"\n{COLORS['RED']}{COLORS['BOLD']}Force shutdown requested. Exiting immediately.{COLORS['RESET']}"
            )
            sys.exit(1)

        self.shutdown_requested = True
        print(
            f"\n{COLORS['YELLOW']}{COLORS['BOLD']}Shutdown requested ({signal_name}). "
            f"Finishing current test...{COLORS['RESET']}"
        )
        print(
            f"{COLORS['YELLOW']}Press Ctrl+C again to force quit.{COLORS['RESET']}"
        )

    def save_partial_results(self):
        """Save partial results if any tests were completed."""
        if self.results and self.agent_mode:
            print(
                f"\n{COLORS['CYAN']}Saving partial results...{COLORS['RESET']}"
            )
            return generate_aivss_report(self.results, self.agent_mode, partial=True)
        return None


shutdown_handler = ShutdownHandler()


def print_banner():
    banner = f"""

{COLORS["RED"]}
     )            (            (                  )          )   *           (        )
  ( /(            )\\ )   (     )\\ )     (      ( /(   (   ( /( (  `    (     )\\ )  ( /(
  )\\())(   (   ( (()/(   )\\   (()/(   ( )\\ (   )\\())  )\\  )\\())\\))(   )\\   (()/(  )\\())
|((_)\\ )\\  )\\  )\\ /(_)|(((_)(  /(_))  )((_))\\ ((_)\\ (((_)((_)\\((_)()((((_)(  /(_))((_)\\
|_ ((_|(_)((_)((_|_))  )\\ _ )\\(_))   ((_)_((_) _((_))\\___ _((_|_()((_)\\ _ )\\(_)) |_ ((_)
| |/ /| __\\ \\ / /| |   (_)_\\(_) _ \\   | _ ) __| \\| ((/ __| || |  \\/  (_)_\\(_) _ \\| |/ /
| ' < | _| \\ V / | |__  / _ \\ |   /   | _ \\ _|| .` || (__| __ | |\\/| |/ _ \\ |   /  ' <
|_|\\_\\|___| \\_/  |____|/_/ \\_\\|_|_\\   |___/___|_|\\_| \\___|_||_|_|  |_/_/ \\_\\|_|_\\ _|\\_\\
                                                                                         {COLORS["RESET"]}

{COLORS["WHITE"]}{COLORS["BOLD"]}Kevlar: OWASP Top 10 for Agentic Apps 2026 Benchmark{COLORS["RESET"]}
{COLORS["CYAN"]}A Red Team Tool for AI Agent Security Testing{COLORS["RESET"]}
{COLORS["YELLOW"]}Version 1.1 | MIT License | Author: toxy4ny{COLORS["RESET"]}
{COLORS["WHITE"]}https://github.com/toxy4ny/kevlar-benchmark{COLORS["RESET"]}
"""
    print(banner)


def select_asis() -> List[str]:
    asis = [
        ("ASI01", "Agent Goal Hijack"),
        ("ASI02", "Tool Misuse and Exploitation"),
        ("ASI03", "Identity and Privilege Abuse"),
        ("ASI04", "Agentic Supply Chain Vulnerabilities"),
        ("ASI05", "Unexpected Code Execution (RCE)"),
        ("ASI06", "Memory and Context Poisoning"),
        ("ASI07", "Insecure Inter-Agent Communication"),
        ("ASI08", "Cascading Failures"),
        ("ASI09", "Human-Agent Trust Exploitation"),
        ("ASI10", "Rogue Agents"),
    ]

    print(f"\n{COLORS['CYAN']}{COLORS['BOLD']}Select ASI Tests:{COLORS['RESET']}")
    print(
        f"{COLORS['WHITE']}Enter numbers separated by commas, or 'all' for all tests, 'custom' for manual selection.{COLORS['RESET']}"
    )

    for i, (asi_id, description) in enumerate(asis, 1):
        print(f"  {COLORS['GREEN']}{i}.{COLORS['RESET']} {asi_id}: {description}")

    choice = (
        input(f"\n{COLORS['YELLOW']}Your choice: {COLORS['RESET']}").strip().lower()
    )

    if choice == "all":
        return [asi_id for asi_id, _ in asis]
    elif choice == "custom":
        selected = []
        while True:
            try:
                num = int(
                    input(
                        f"{COLORS['YELLOW']}Enter ASI number (0 to finish): {COLORS['RESET']}"
                    )
                )
                if num == 0:
                    break
                if 1 <= num <= len(asis):
                    selected.append(asis[num - 1][0])
                    print(
                        f"{COLORS['GREEN']}Added {asis[num - 1][0]}{COLORS['RESET']}"
                    )
                else:
                    print(f"{COLORS['RED']}Invalid number{COLORS['RESET']}")
            except ValueError:
                print(f"{COLORS['RED']}Please enter a number{COLORS['RESET']}")
        return selected
    else:
        try:
            nums = [int(x.strip()) for x in choice.split(",")]
            return [asis[n - 1][0] for n in nums if 1 <= n <= len(asis)]
        except Exception:
            print(
                f"{COLORS['RED']}Invalid input. Defaulting to ASI01{COLORS['RESET']}"
            )
            return ["ASI01"]


def select_mode() -> str:
    print(f"\n{COLORS['CYAN']}{COLORS['BOLD']}Select Agent Mode:{COLORS['RESET']}")
    print(f"  {COLORS['GREEN']}1.{COLORS['RESET']} Mock Agent (Safe for learning)")
    print(
        f"  {COLORS['YELLOW']}2.{COLORS['RESET']} Real Agent (LangChain/AutoGen + Ollama)"
    )

    while True:
        choice = input(f"\n{COLORS['YELLOW']}Mode (1/2): {COLORS['RESET']}").strip()
        if choice == "1":
            return "mock"
        elif choice == "2":
            return "real"
        else:
            print(f"{COLORS['RED']}Invalid choice{COLORS['RESET']}")


def create_agent(mode: str):
    if mode == "mock":
        print(f"{COLORS['GREEN']}Using Mock Agent (safe mode){COLORS['RESET']}")
        return MockCopilotAgent()
    else:
        print(
            f"{COLORS['YELLOW']}Initializing Real LangChain Agent...{COLORS['RESET']}"
        )
        return RealLangChainAgent(model_name="llama3.1")


def run_asi_test(asi_id: str, agent, results: Dict[str, Any]):
    print(f"\n{COLORS['BLUE']}{COLORS['BOLD']}Running {asi_id}...{COLORS['RESET']}")

    start_time = time.time()

    try:
        if asi_id == "ASI01":
            orchestrator = GoalHijackOrchestrator(
                agent, config={"auto_stop_on_critical": False}
            )
        elif asi_id == "ASI02":
            orchestrator = ToolAbuseOrchestrator(
                agent, config={"auto_stop_on_critical": False}
            )
        elif asi_id == "ASI03":
            orchestrator = IdentityOrchestrator(
                agent, config={"auto_stop_on_critical": False}
            )
        elif asi_id == "ASI04":
            orchestrator = SupplyChainOrchestrator(
                agent, config={"auto_stop_on_critical": False}
            )
        elif asi_id == "ASI05":
            orchestrator = RCEOrchestrator(
                agent, config={"auto_stop_on_critical": False}
            )
        elif asi_id == "ASI06":
            orchestrator = MemoryPoisoningOrchestrator(
                agent, config={"auto_stop_on_critical": False}
            )
        elif asi_id == "ASI07":
            orchestrator = InterAgentOrchestrator(
                agent, config={"auto_stop_on_critical": False}
            )
        elif asi_id == "ASI08":
            orchestrator = CascadingOrchestrator(
                agent, config={"auto_stop_on_critical": False}
            )
        elif asi_id == "ASI09":
            orchestrator = HumanTrustOrchestrator(
                agent, config={"auto_stop_on_critical": False}
            )
        elif asi_id == "ASI10":
            orchestrator = RogueAgentOrchestrator(
                agent, config={"auto_stop_on_critical": False}
            )
        else:
            raise ValueError(f"Unknown ASI: {asi_id}")

        if hasattr(orchestrator, "run_all_tests"):
            results_list = orchestrator.run_all_tests()
        elif hasattr(orchestrator, "run_all_scenarios"):
            results_list = orchestrator.run_all_scenarios()
        else:
            raise AttributeError(f"Orchestrator for {asi_id} has no run method")

        vulnerable_count = sum(1 for r in results_list if r.get("vulnerable", False))
        total_count = len(results_list)

        end_time = time.time()
        duration = end_time - start_time

        results[asi_id] = {
            "vulnerable_count": vulnerable_count,
            "total_count": total_count,
            "duration": duration,
            "results": results_list,
        }

        if vulnerable_count > 0:
            print(
                f"{COLORS['RED']}{COLORS['BOLD']}{vulnerable_count}/{total_count} vulnerabilities found in {asi_id} ({duration:.2f}s){COLORS['RESET']}"
            )
        else:
            print(
                f"{COLORS['GREEN']}{COLORS['BOLD']}No vulnerabilities found in {asi_id} ({duration:.2f}s){COLORS['RESET']}"
            )

    except Exception as e:
        print(f"{COLORS['RED']}Error running {asi_id}: {e}{COLORS['RESET']}")
        results[asi_id] = {"error": str(e), "duration": time.time() - start_time}


def generate_aivss_report(results: Dict[str, Any], agent_mode: str, partial: bool = False):
    report = {
        "aivss_version": "1.0",
        "benchmark": {
            "name": "Kevlar",
            "version": "1.1",
            "url": "https://github.com/toxy4ny/kevlar-benchmark",
        },
        "agent": {
            "mode": agent_mode,
            "model": "llama3.1" if agent_mode == "real" else "MockCopilotAgent",
        },
        "scan": {
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": 0,
            "tested_asis": list(results.keys()),
            "total_vulnerabilities": 0,
            "critical_vulnerabilities": 0,
            "high_vulnerabilities": 0,
            "medium_vulnerabilities": 0,
            "low_vulnerabilities": 0,
        },
        "findings": [],
    }

    total_duration = 0
    total_vulns = 0
    critical_vulns = 0
    high_vulns = 0
    medium_vulns = 0

    for asi_id, result in results.items():
        if "error" in result:
            continue

        total_duration += result["duration"]
        total_vulns += result["vulnerable_count"]

        for finding in result["results"]:
            severity = finding.get("severity", "NONE")
            if severity == "CRITICAL":
                critical_vulns += 1
            elif severity == "HIGH":
                high_vulns += 1
            elif severity == "MEDIUM":
                medium_vulns += 1

        for finding in result["results"]:
            report["findings"].append(
                {
                    "asi_id": asi_id,
                    "scenario": finding.get("scenario", ""),
                    "severity": finding.get("severity", "NONE"),
                    "evidence": finding.get("evidence", ""),
                    "timestamp": datetime.now().isoformat(),
                }
            )

    report["scan"]["end_time"] = datetime.now().isoformat()
    report["scan"]["duration_seconds"] = total_duration
    report["scan"]["total_vulnerabilities"] = total_vulns
    report["scan"]["critical_vulnerabilities"] = critical_vulns
    report["scan"]["high_vulnerabilities"] = high_vulns
    report["scan"]["medium_vulnerabilities"] = medium_vulns
    report["scan"]["partial"] = partial

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "_partial" if partial else ""
    filename = f"reports/kevlar_aivss_report_{timestamp}{suffix}.json"
    os.makedirs("reports", exist_ok=True)

    with open(filename, "w") as f:
        json.dump(report, f, indent=2)

    print(
        f"\n{COLORS['CYAN']}{COLORS['BOLD']}Report generated: {filename}{COLORS['RESET']}"
    )
    print(
        f"{COLORS['WHITE']}Total vulnerabilities: {total_vulns} (Critical: {critical_vulns}, High: {high_vulns}, Medium: {medium_vulns}){COLORS['RESET']}"
    )

    return filename


def main():
    """Main entry point for Kevlar CLI."""
    shutdown_handler.install()

    try:
        print_banner()

        selected_asis = select_asis()
        print(
            f"\n{COLORS['GREEN']}Selected ASI: {', '.join(selected_asis)}{COLORS['RESET']}"
        )

        mode = select_mode()
        shutdown_handler.agent_mode = mode
        agent = create_agent(mode)

        results = {}
        shutdown_handler.results = results
        print(
            f"\n{COLORS['YELLOW']}{COLORS['BOLD']}Starting Kevlar Scan...{COLORS['RESET']}"
        )

        for asi_id in selected_asis:
            if shutdown_handler.shutdown_requested:
                print(
                    f"\n{COLORS['YELLOW']}Skipping remaining tests due to shutdown request.{COLORS['RESET']}"
                )
                break

            shutdown_handler.current_asi = asi_id
            run_asi_test(asi_id, agent, results)

        if shutdown_handler.shutdown_requested:
            report_file = shutdown_handler.save_partial_results()
            print(
                f"\n{COLORS['YELLOW']}{COLORS['BOLD']}Kevlar Scan Interrupted.{COLORS['RESET']}"
            )
            if report_file:
                print(
                    f"{COLORS['WHITE']}Partial report saved to: {report_file}{COLORS['RESET']}"
                )
        else:
            report_file = generate_aivss_report(results, mode)
            print(
                f"\n{COLORS['MAGENTA']}{COLORS['BOLD']}Kevlar Scan Complete!{COLORS['RESET']}"
            )
            print(f"{COLORS['WHITE']}Report saved to: {report_file}{COLORS['RESET']}")

        print(
            f"{COLORS['CYAN']}Thank you for using Kevlar - Red Team Tool for AI Agent Security{COLORS['RESET']}"
        )
        print(
            f"{COLORS['WHITE']}Run 'kevlar' again to test more agents or different ASI combinations{COLORS['RESET']}"
        )

    except KeyboardInterrupt:
        print(
            f"\n{COLORS['YELLOW']}Interrupted during setup.{COLORS['RESET']}"
        )
        sys.exit(130)
    finally:
        shutdown_handler.uninstall()


if __name__ == "__main__":
    main()
