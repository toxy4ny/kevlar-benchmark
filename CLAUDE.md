# Kevlar

## Project Overview

Kevlar is a red team security benchmark for testing AI agents against the OWASP Top 10 for Agentic Applications (2026). It implements 10 ASI (Agent-Specific Injection) vulnerability tests ordered by criticality.

## Critical Workflow Rules

### Git Conventions

- Commit messages пишутся на **русском языке**
- Группировать изменения в разные коммиты по смыслу
- **НЕ добавлять** "Generated with Claude Code" в commit messages
- Main branch для PR: `main`

## Commands

```bash
# Install dependencies
uv sync

# Run full benchmark (interactive mode)
uv run kevlar
# Or: uv run python -m kevlar.cli

# Run individual ASI test scripts
uv run python scripts/run_asi01.py   # Agent Goal Hijack
uv run python scripts/run_asi02.py   # Tool Misuse
uv run python scripts/run_asi03.py   # Identity Abuse
uv run python scripts/run_asi04.py   # Supply Chain
uv run python scripts/run_asi05.py   # RCE
uv run python scripts/run_asi06.py   # Memory Poisoning
uv run python scripts/run_asi07.py   # Inter-Agent Comms
uv run python scripts/run_asi08.py   # Cascading Failures
uv run python scripts/run_asi09.py   # Human Trust
uv run python scripts/run_asi10.py   # Rogue Agents

# Run tests
uv run pytest tests/                    # All tests
uv run pytest tests/unit/               # Unit tests only
uv run pytest tests/integration/        # Integration tests only
uv run pytest tests/ -v --tb=short      # Verbose with short traceback
```

## Testing

### Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── integration/                   # Integration tests
│   ├── test_orchestrator_pipeline.py
│   └── test_runner_cli.py
└── unit/                          # Unit tests
    ├── critical/                  # ASI01-ASI05 tests
    │   ├── asi01_goal_hijack/
    │   ├── asi02_tool_abuse/
    │   ├── asi03_identity_abuse/
    │   ├── asi04_supply_chain/
    │   └── asi05_rce/
    ├── high/                      # ASI06-ASI08 tests
    │   ├── asi06_memory_poisoning/
    │   ├── asi07_inter_agent_comms/
    │   └── asi08_cascading_failures/
    ├── medium/                    # ASI09-ASI10 tests
    │   ├── asi09_human_trust/
    │   └── asi10_rogue_agents/
    ├── test_kevlar_types.py
    ├── test_local_agent.py
    ├── test_langchain_asi02_adapter.py
    ├── test_langchain_asi04_adapter.py
    ├── test_real_agent_adapter.py
    ├── test_runner.py
    └── test_threat_orchestrator.py
```

### Test Stats

- **591 tests** total
- **Coverage: ~56%** (threshold: 40%)
- Unit tests for all 10 ASI modules
- Integration tests for CLI and orchestrator pipeline

### Key Fixtures (conftest.py)

- `mock_agent` - MockCopilotAgent instance
- `mock_langchain_agent` - Mocked RealLangChainAgent
- `empty_session_log`, `vulnerable_session_log`, `safe_session_log` - SessionLog variants
- `malicious_email`, `safe_email` - Email payloads
- `shell_injection_payload`, `sql_injection_payload` - Attack payloads
- `malicious_mcp_descriptor`, `valid_mcp_descriptor` - MCP descriptors

## Architecture

### Project Structure (src layout)

```
kevlar-benchmark/
├── pyproject.toml
├── README.md, CLAUDE.md
├── src/kevlar/
│   ├── __init__.py
│   ├── cli.py                     # Main CLI entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py        # ThreatOrchestrator
│   │   └── types.py               # SessionLog dataclass
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── protocol.py            # AgentProtocol (typing)
│   │   ├── mock.py                # MockCopilotAgent
│   │   ├── langchain.py           # RealLangChainAgent
│   │   └── adapters/
│   │       ├── asi02.py           # LangChainASI02Agent
│   │       └── asi04.py           # LangChainASI04Agent
│   └── modules/                   # ASI test modules
│       ├── critical/              # ASI01-ASI05
│       ├── high/                  # ASI06-ASI08
│       └── medium/                # ASI09-ASI10
├── scripts/
│   └── run_asi*.py                # Individual ASI runners
└── tests/                         # pytest tests
```

### Core Components

- `src/kevlar/cli.py` - Main CLI entry point (`kevlar` command)
- `src/kevlar/core/orchestrator.py` - Central dispatcher that runs ASI modules in risk order
- `src/kevlar/core/types.py` - `SessionLog` dataclass capturing all benchmark artifacts

### Agent Adapters

All agents implement `AgentProtocol` (see `src/kevlar/agents/protocol.py`):

- `src/kevlar/agents/mock.py` - `MockCopilotAgent` for safe testing
- `src/kevlar/agents/langchain.py` - `RealLangChainAgent` for LLM testing
- `src/kevlar/agents/adapters/` - Specialized adapters for specific ASI tests

### ASI Modules Structure

Modules are organized by criticality under `src/kevlar/modules/`:

```
modules/
├── critical/          # ASI01-ASI05 (highest risk)
│   ├── asi01_goal_hijack/
│   │   ├── attacks/       # EchoLeak, Operator, Inception, GoalDrift
│   │   ├── detectors/     # DataExfilDetector, GoalDriftAnalyzer
│   │   └── utils/
│   ├── asi02_tool_abuse/
│   ├── asi03_identity_abuse/
│   ├── asi04_supply_chain/
│   └── asi05_rce/
├── high/              # ASI06-ASI08
│   ├── asi06_memory_poisoning/
│   ├── asi07_inter_agent_comms/
│   └── asi08_cascading_failures/
└── medium/            # ASI09-ASI10
    ├── asi09_human_trust/
    └── asi10_rogue_agents/
```

Each ASI module follows the pattern:
- `*Orchestrator` class with `run_all_scenarios()` or `run_all_tests()` method
- `attacks/` subdirectory with attack simulators
- `detectors/` subdirectory with vulnerability detection logic

### Imports

Use the new kevlar.* import paths:

```python
# Core types
from kevlar.core.types import SessionLog
from kevlar.core import ThreatOrchestrator

# Agents
from kevlar.agents import MockCopilotAgent, RealLangChainAgent, AgentProtocol
from kevlar.agents.adapters import LangChainASI02Agent, LangChainASI04Agent

# Modules
from kevlar.modules.critical.asi01_goal_hijack import GoalHijackOrchestrator
```

### Output

Reports are generated as JSON in `reports/kevlar_aivss_report_<timestamp>.json` following OWASP AIVSS scoring format.
