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
from typing import Any, Dict, List, Optional, Tuple

import click

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

__version__ = "1.2"

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

ALL_ASIS = [
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

# Exit codes for CI mode
EXIT_SUCCESS = 0
EXIT_VULNS_FOUND = 1
EXIT_CRITICAL_VULNS = 2
EXIT_INTERRUPTED = 130


class ShutdownHandler:
    """Handles graceful shutdown on SIGINT/SIGTERM."""

    def __init__(self):
        self.shutdown_requested = False
        self.current_asi: Optional[str] = None
        self.results: Dict[str, Any] = {}
        self.agent_mode: Optional[str] = None
        self.model_name: Optional[str] = None
        self.quiet: bool = False
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
            if not self.quiet:
                print(
                    f"\n{COLORS['RED']}{COLORS['BOLD']}Force shutdown requested. Exiting immediately.{COLORS['RESET']}"
                )
            sys.exit(1)

        self.shutdown_requested = True
        if not self.quiet:
            print(
                f"\n{COLORS['YELLOW']}{COLORS['BOLD']}Shutdown requested ({signal_name}). "
                f"Finishing current test...{COLORS['RESET']}"
            )
            print(
                f"{COLORS['YELLOW']}Press Ctrl+C again to force quit.{COLORS['RESET']}"
            )

    def save_partial_results(self, output_path: Optional[str] = None):
        """Save partial results if any tests were completed."""
        if self.results and self.agent_mode:
            if not self.quiet:
                print(f"\n{COLORS['CYAN']}Saving partial results...{COLORS['RESET']}")
            return generate_aivss_report(
                self.results,
                self.agent_mode,
                self.model_name,
                partial=True,
                output_path=output_path,
                quiet=self.quiet,
            )
        return None


shutdown_handler = ShutdownHandler()


def get_colors(quiet: bool) -> Dict[str, str]:
    """Return colors dict, empty strings if quiet mode."""
    if quiet:
        return {k: "" for k in COLORS}
    return COLORS


def print_banner(quiet: bool = False):
    if quiet:
        return

    colors = get_colors(quiet)
    banner = f"""

{colors["RED"]}
     )            (            (                  )          )   *           (        )
  ( /(            )\\ )   (     )\\ )     (      ( /(   (   ( /( (  `    (     )\\ )  ( /(
  )\\())(   (   ( (()/(   )\\   (()/(   ( )\\ (   )\\())  )\\  )\\())\\))(   )\\   (()/(  )\\())
|((_)\\ )\\  )\\  )\\ /(_)|(((_)(  /(_))  )((_))\\ ((_)\\ (((_)((_)\\((_)()((((_)(  /(_))((_)\\
|_ ((_|(_)((_)((_|_))  )\\ _ )\\(_))   ((_)_((_) _((_))\\___ _((_|_()((_)\\ _ )\\(_)) |_ ((_)
| |/ /| __\\ \\ / /| |   (_)_\\(_) _ \\   | _ ) __| \\| ((/ __| || |  \\/  (_)_\\(_) _ \\| |/ /
| ' < | _| \\ V / | |__  / _ \\ |   /   | _ \\ _|| .` || (__| __ | |\\/| |/ _ \\ |   /  ' <
|_|\\_\\|___| \\_/  |____|/_/ \\_\\|_|_\\   |___/___|_|\\_| \\___|_||_|_|  |_/_/ \\_\\|_|_\\ _|\\_\\
                                                                                         {colors["RESET"]}

{colors["WHITE"]}{colors["BOLD"]}Kevlar: OWASP Top 10 for Agentic Apps 2026 Benchmark{colors["RESET"]}
{colors["CYAN"]}A Red Team Tool for AI Agent Security Testing{colors["RESET"]}
{colors["YELLOW"]}Version {__version__} | MIT License | Author: toxy4ny{colors["RESET"]}
{colors["WHITE"]}https://github.com/toxy4ny/kevlar-benchmark{colors["RESET"]}
"""
    print(banner)


def select_asis_interactive() -> List[str]:
    """Interactive ASI selection menu."""
    colors = get_colors(False)

    print(f"\n{colors['CYAN']}{colors['BOLD']}Select ASI Tests:{colors['RESET']}")
    print(
        f"{colors['WHITE']}Enter numbers separated by commas, or 'all' for all tests, 'custom' for manual selection.{colors['RESET']}"
    )

    for i, (asi_id, description) in enumerate(ALL_ASIS, 1):
        print(f"  {colors['GREEN']}{i}.{colors['RESET']} {asi_id}: {description}")

    choice = (
        input(f"\n{colors['YELLOW']}Your choice: {colors['RESET']}").strip().lower()
    )

    if choice == "all":
        return [asi_id for asi_id, _ in ALL_ASIS]
    elif choice == "custom":
        selected = []
        while True:
            try:
                num = int(
                    input(
                        f"{colors['YELLOW']}Enter ASI number (0 to finish): {colors['RESET']}"
                    )
                )
                if num == 0:
                    break
                if 1 <= num <= len(ALL_ASIS):
                    selected.append(ALL_ASIS[num - 1][0])
                    print(
                        f"{colors['GREEN']}Added {ALL_ASIS[num - 1][0]}{colors['RESET']}"
                    )
                else:
                    print(f"{colors['RED']}Invalid number{colors['RESET']}")
            except ValueError:
                print(f"{colors['RED']}Please enter a number{colors['RESET']}")
        return selected
    else:
        try:
            nums = [int(x.strip()) for x in choice.split(",")]
            return [ALL_ASIS[n - 1][0] for n in nums if 1 <= n <= len(ALL_ASIS)]
        except Exception:
            print(f"{colors['RED']}Invalid input. Defaulting to ASI01{colors['RESET']}")
            return ["ASI01"]


def select_mode_interactive() -> str:
    """Interactive agent mode selection."""
    colors = get_colors(False)

    print(f"\n{colors['CYAN']}{colors['BOLD']}Select Agent Mode:{colors['RESET']}")
    print(f"  {colors['GREEN']}1.{colors['RESET']} Mock Agent (Safe for learning)")
    print(
        f"  {colors['YELLOW']}2.{colors['RESET']} Real Agent (LangChain/AutoGen + Ollama)"
    )

    while True:
        choice = input(f"\n{colors['YELLOW']}Mode (1/2): {colors['RESET']}").strip()
        if choice == "1":
            return "mock"
        elif choice == "2":
            return "real"
        else:
            print(f"{colors['RED']}Invalid choice{colors['RESET']}")


def parse_asi_args(asi_args: Tuple[str, ...]) -> List[str]:
    """Parse ASI arguments to list of ASI IDs."""
    valid_asis = {asi_id for asi_id, _ in ALL_ASIS}
    result = []

    for arg in asi_args:
        # Normalize to uppercase
        asi = arg.upper()
        if asi in valid_asis:
            if asi not in result:
                result.append(asi)
        else:
            raise click.BadParameter(
                f"Unknown ASI: {arg}. Valid: {', '.join(sorted(valid_asis))}"
            )

    return result


def create_agent(mode: str, model: str = "llama3.1:8b", quiet: bool = False):
    """Create agent based on mode. Fails if real mode deps unavailable."""
    colors = get_colors(quiet)

    if mode == "mock":
        if not quiet:
            print(f"{colors['GREEN']}Using Mock Agent (safe mode){colors['RESET']}")
        return MockCopilotAgent()

    # Real mode - check dependencies
    from kevlar.agents import check_real_agent_dependencies

    deps = check_real_agent_dependencies(model=model)

    if not deps["available"]:
        missing_str = "\n  - ".join(deps["missing"])
        raise click.ClickException(
            f"Real agent mode requires:\n  - {missing_str}\n\n"
            "Use --mode mock for safe testing without external dependencies."
        )

    if not quiet:
        print(
            f"{colors['YELLOW']}Initializing Real LangChain Agent (model: {model})...{colors['RESET']}"
        )
    return RealLangChainAgent(model_name=model)


def check_dependencies_and_exit(quiet: bool = False):
    """Check agent dependencies and exit with appropriate code."""
    from kevlar.agents import check_real_agent_dependencies

    colors = get_colors(quiet)
    deps = check_real_agent_dependencies()

    print(
        f"\n{colors['CYAN']}{colors['BOLD']}Kevlar Dependency Check{colors['RESET']}\n"
    )

    def status(ok: bool) -> str:
        if ok:
            return f"{colors['GREEN']}[OK]{colors['RESET']}"
        return f"{colors['RED']}[MISSING]{colors['RESET']}"

    print(f"  {status(deps['langchain'])} LangChain")
    print(f"  {status(deps['ollama'])} Ollama")

    print()
    if deps["available"]:
        print(f"{colors['GREEN']}Real agent mode: available{colors['RESET']}")
        sys.exit(0)
    else:
        print(f"{colors['RED']}Real agent mode: NOT available{colors['RESET']}")
        for m in deps["missing"]:
            print(f"  {colors['YELLOW']}{m}{colors['RESET']}")
        sys.exit(1)


def run_asi_test(asi_id: str, agent, results: Dict[str, Any], quiet: bool = False):
    """Run a single ASI test."""
    colors = get_colors(quiet)

    if not quiet:
        print(f"\n{colors['BLUE']}{colors['BOLD']}Running {asi_id}...{colors['RESET']}")

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

        if not quiet:
            if vulnerable_count > 0:
                print(
                    f"{colors['RED']}{colors['BOLD']}{vulnerable_count}/{total_count} vulnerabilities found in {asi_id} ({duration:.2f}s){colors['RESET']}"
                )
            else:
                print(
                    f"{colors['GREEN']}{colors['BOLD']}No vulnerabilities found in {asi_id} ({duration:.2f}s){colors['RESET']}"
                )

    except Exception as e:
        if not quiet:
            print(f"{colors['RED']}Error running {asi_id}: {e}{colors['RESET']}")
        results[asi_id] = {"error": str(e), "duration": time.time() - start_time}


def generate_aivss_report(
    results: Dict[str, Any],
    agent_mode: str,
    model_name: Optional[str] = None,
    partial: bool = False,
    output_path: Optional[str] = None,
    quiet: bool = False,
) -> str:
    """Generate AIVSS report."""
    colors = get_colors(quiet)

    if model_name is None:
        model_name = "llama3.1:8b" if agent_mode == "real" else "MockCopilotAgent"

    report = {
        "aivss_version": "1.0",
        "benchmark": {
            "name": "Kevlar",
            "version": __version__,
            "url": "https://github.com/toxy4ny/kevlar-benchmark",
        },
        "agent": {
            "mode": agent_mode,
            "model": model_name if agent_mode == "real" else "MockCopilotAgent",
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

    if output_path:
        filename = output_path
        # Ensure parent directory exists
        parent_dir = os.path.dirname(filename)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = "_partial" if partial else ""
        filename = f"reports/kevlar_aivss_report_{timestamp}{suffix}.json"
        os.makedirs("reports", exist_ok=True)

    with open(filename, "w") as f:
        json.dump(report, f, indent=2)

    if not quiet:
        print(
            f"\n{colors['CYAN']}{colors['BOLD']}Report generated: {filename}{colors['RESET']}"
        )
        print(
            f"{colors['WHITE']}Total vulnerabilities: {total_vulns} (Critical: {critical_vulns}, High: {high_vulns}, Medium: {medium_vulns}){colors['RESET']}"
        )

    return filename


def determine_exit_code(results: Dict[str, Any]) -> int:
    """Determine exit code based on results for CI mode."""
    has_critical = False
    has_vulns = False

    for asi_id, result in results.items():
        if "error" in result:
            continue

        if result.get("vulnerable_count", 0) > 0:
            has_vulns = True

        for finding in result.get("results", []):
            if finding.get("severity") == "CRITICAL":
                has_critical = True
                break

        if has_critical:
            break

    if has_critical:
        return EXIT_CRITICAL_VULNS
    elif has_vulns:
        return EXIT_VULNS_FOUND
    return EXIT_SUCCESS


def run_interactive_mode():
    """Run Kevlar in interactive mode."""
    print_banner()

    selected_asis = select_asis_interactive()
    colors = get_colors(False)
    print(
        f"\n{colors['GREEN']}Selected ASI: {', '.join(selected_asis)}{colors['RESET']}"
    )

    mode = select_mode_interactive()
    shutdown_handler.agent_mode = mode
    shutdown_handler.model_name = "llama3.1:8b" if mode == "real" else None
    agent = create_agent(mode)

    results = {}
    shutdown_handler.results = results
    print(
        f"\n{colors['YELLOW']}{colors['BOLD']}Starting Kevlar Scan...{colors['RESET']}"
    )

    for asi_id in selected_asis:
        if shutdown_handler.shutdown_requested:
            print(
                f"\n{colors['YELLOW']}Skipping remaining tests due to shutdown request.{colors['RESET']}"
            )
            break

        shutdown_handler.current_asi = asi_id
        run_asi_test(asi_id, agent, results)

    if shutdown_handler.shutdown_requested:
        report_file = shutdown_handler.save_partial_results()
        print(
            f"\n{colors['YELLOW']}{colors['BOLD']}Kevlar Scan Interrupted.{colors['RESET']}"
        )
        if report_file:
            print(
                f"{colors['WHITE']}Partial report saved to: {report_file}{colors['RESET']}"
            )
    else:
        report_file = generate_aivss_report(results, mode, shutdown_handler.model_name)
        print(
            f"\n{colors['MAGENTA']}{colors['BOLD']}Kevlar Scan Complete!{colors['RESET']}"
        )
        print(f"{colors['WHITE']}Report saved to: {report_file}{colors['RESET']}")

    print(
        f"{colors['CYAN']}Thank you for using Kevlar - Red Team Tool for AI Agent Security{colors['RESET']}"
    )
    print(
        f"{colors['WHITE']}Run 'kevlar' again to test more agents or different ASI combinations{colors['RESET']}"
    )


def run_noninteractive_mode(
    asi_list: List[str],
    mode: str,
    model: str,
    output: Optional[str],
    quiet: bool,
    ci: bool,
) -> int:
    """Run Kevlar in non-interactive mode. Returns exit code."""
    colors = get_colors(quiet)

    if not quiet:
        print_banner()
        print(
            f"\n{colors['GREEN']}Selected ASI: {', '.join(asi_list)}{colors['RESET']}"
        )

    shutdown_handler.agent_mode = mode
    shutdown_handler.model_name = model if mode == "real" else None
    shutdown_handler.quiet = quiet

    agent = create_agent(mode, model, quiet)

    results = {}
    shutdown_handler.results = results

    if not quiet:
        print(
            f"\n{colors['YELLOW']}{colors['BOLD']}Starting Kevlar Scan...{colors['RESET']}"
        )

    for asi_id in asi_list:
        if shutdown_handler.shutdown_requested:
            if not quiet:
                print(
                    f"\n{colors['YELLOW']}Skipping remaining tests due to shutdown request.{colors['RESET']}"
                )
            break

        shutdown_handler.current_asi = asi_id
        run_asi_test(asi_id, agent, results, quiet)

    if shutdown_handler.shutdown_requested:
        report_file = shutdown_handler.save_partial_results(output)
        if not quiet:
            print(
                f"\n{colors['YELLOW']}{colors['BOLD']}Kevlar Scan Interrupted.{colors['RESET']}"
            )
            if report_file:
                print(
                    f"{colors['WHITE']}Partial report saved to: {report_file}{colors['RESET']}"
                )
        return EXIT_INTERRUPTED

    report_file = generate_aivss_report(
        results, mode, shutdown_handler.model_name, output_path=output, quiet=quiet
    )

    if not quiet:
        print(
            f"\n{colors['MAGENTA']}{colors['BOLD']}Kevlar Scan Complete!{colors['RESET']}"
        )
        print(f"{colors['WHITE']}Report saved to: {report_file}{colors['RESET']}")

    if ci:
        return determine_exit_code(results)

    return EXIT_SUCCESS


@click.command()
@click.option(
    "--asi",
    "-a",
    multiple=True,
    help="ASI tests to run (e.g., ASI01, ASI05). Can be specified multiple times.",
)
@click.option("--all", "run_all", is_flag=True, help="Run all ASI tests.")
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["mock", "real"]),
    default="mock",
    help="Agent mode: mock (safe) or real (LangChain + Ollama).",
)
@click.option(
    "--model", default="llama3.1:8b", help="Model name for real agent (default: llama3.1:8b)."
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output report path (default: reports/kevlar_aivss_report_<timestamp>.json).",
)
@click.option("--quiet", "-q", is_flag=True, help="Suppress banner and colors.")
@click.option(
    "--ci",
    is_flag=True,
    help="CI mode: quiet + exit code based on severity (0=safe, 1=vulns, 2=critical).",
)
@click.option("--check", is_flag=True, help="Check agent dependencies and exit.")
@click.version_option(version=__version__, prog_name="kevlar")
def main(asi, run_all, mode, model, output, quiet, ci, check):
    """Kevlar: OWASP Top 10 for Agentic Apps 2026 Benchmark.

    Red Team Tool for AI Agent Security Testing.

    Examples:

    \b
      # Interactive mode (default)
      kevlar

    \b
      # Run specific ASI tests
      kevlar --asi ASI01 --asi ASI05 --mode mock

    \b
      # Run all tests with real agent
      kevlar --all --mode real --model llama3.1:8b

    \b
      # CI mode with custom output
      kevlar --all --ci --output report.json
    """
    # Handle --check before anything else
    if check:
        check_dependencies_and_exit(quiet)
        return

    shutdown_handler.install()

    try:
        # Determine if we're in non-interactive mode
        has_cli_args = bool(asi) or run_all

        if has_cli_args:
            # Non-interactive mode
            if ci:
                quiet = True  # CI mode implies quiet

            if run_all:
                asi_list = [asi_id for asi_id, _ in ALL_ASIS]
            else:
                asi_list = parse_asi_args(asi)

            if not asi_list:
                raise click.UsageError("No ASI tests specified. Use --asi or --all.")

            exit_code = run_noninteractive_mode(
                asi_list, mode, model, output, quiet, ci
            )
            sys.exit(exit_code)
        else:
            # Interactive mode
            run_interactive_mode()

    except KeyboardInterrupt:
        colors = get_colors(quiet if "quiet" in dir() else False)
        print(f"\n{colors['YELLOW']}Interrupted during setup.{colors['RESET']}")
        sys.exit(EXIT_INTERRUPTED)
    finally:
        shutdown_handler.uninstall()


if __name__ == "__main__":
    main()
