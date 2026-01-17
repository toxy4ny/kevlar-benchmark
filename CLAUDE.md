# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kevlar is a red team security benchmark for testing AI agents against the OWASP Top 10 for Agentic Applications (2026). It implements 10 ASI (Agent-Specific Injection) vulnerability tests ordered by criticality.

## Critical Workflow Rules

### Issue Tracking with bd (beads)

- **ALWAYS** use bd for task and issue tracking: `bd onboard` для начала
- Перед завершением сессии: создать issues для незавершённой работы, закрыть завершённые задачи, синхронизировать с git
- **MANDATORY**: работа НЕ завершена пока не выполнен `git push` (см. AGENTS.md для полного workflow)

### Git Conventions

- Commit messages пишутся на **русском языке**
- Группировать изменения в разные коммиты по смыслу
- **НЕ добавлять** "Generated with Claude Code" в commit messages
- Main branch для PR: `main`

### Documentation Tools

- **ALWAYS** используйте Ref (mcp__Ref__ref_search_documentation) при работе с библиотеками для проверки актуальной документации

## Commands

```bash
# Install dependencies
uv sync

# Run full benchmark (interactive mode)
uv run python runner.py

# Run individual ASI test modules
uv run python test_asi01.py   # Agent Goal Hijack
uv run python test_asi02.py   # Tool Misuse
uv run python test_asi03.py   # Identity Abuse
uv run python test_asi04.py   # Supply Chain
uv run python test_asi05.py   # RCE
uv run python test_asi06.py   # Memory Poisoning
uv run python test_asi07.py   # Inter-Agent Comms
uv run python test_asi08.py   # Cascading Failures
uv run python test_asi09.py   # Human Trust
uv run python test_asi10.py   # Rogue Agents

# Run tests
uv run pytest tests/                    # All tests
uv run pytest tests/unit/               # Unit tests only
uv run pytest tests/integration/        # Integration tests only
uv run pytest tests/ -v --tb=short      # Verbose with short traceback
uv run pytest tests/ --cov=. --cov-report=html  # With coverage report
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
- **Coverage: ~54%** (threshold: 40%)
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

### Core Components

- `runner.py` - Main CLI orchestrator with interactive mode selection (mock vs real agent, ASI selection)
- `core/threat_orchestrator.py` - Central dispatcher that runs ASI modules in risk order
- `kevlar_types.py` - `SessionLog` dataclass capturing all benchmark artifacts (tool calls, network egress, drift scores, etc.)

### Agent Adapters

- `local_agent.py` - `MockCopilotAgent` for safe testing (returns predetermined safe responses)
- `real_agent_adapter.py` - `RealLangChainAgent` integrating LangChain + Ollama for actual LLM testing
- `real_agent.py` - Alternative real agent implementation
- `langchain_asi02_adapter.py`, `langchain_asi04_adapter.py` - Specialized LangChain adapters for specific ASI tests

### ASI Modules Structure

Modules are organized by criticality under `modules/`:

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

### Agent Interface Contract

All agent adapters must implement these methods (see `local_agent.py` for reference):
- `process_email(email)` - Process email input
- `process_rag_query(query, context)` - Handle RAG queries
- `process_document(doc)` - Document processing
- `process_prompt(prompt)` - Generic prompt handling
- `execute_tool_chain(chain)` - Multi-tool execution
- `generate_code(prompt)` - Code generation
- `approve_transaction(**kwargs)` - Transaction approval
- `install_plugin(plugin)` - Plugin installation
- `read_file(path)` - File reading
- `start_session(user_role)` / `execute_with_token(token, action)` - Session handling
- `process_inter_agent_message(msg)` - Inter-agent communication

### Output

Reports are generated as JSON in `reports/kevlar_aivss_report_<timestamp>.json` following OWASP AIVSS scoring format.
