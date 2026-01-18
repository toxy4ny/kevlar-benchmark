# Kevlar: OWASP Top 10 for Agentic Apps 2026 Benchmark

# together with respected people [POXEK AI](https://github.com/szybnev) and [COPYLEFTDEV](https://github.com/copyleftdev)

> **Full-coverage red team framework** for AI agent security testing  
> Based on [OWASP Top 10 for Agentic Applications (2026)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)  
> ✅ Licensed under **CC BY-SA 4.0** | ✅ For **authorized red teaming only**

---

## Mission

Detect, exploit, and report **Agent-Specific Injection (ASI)** vulnerabilities before adversaries do.
Kevlar automates adversarial testing of all **10 OWASP ASI risks**, ordered by real-world criticality from **Appendix D**.

---

## Architecture Overview

```
+-------------------------+
|   Threat Orchestrator   | <- Prioritizes ASI01 -> ASI10
+-----------+-------------+
            |
            v
+-----------------------------------------------------+
|                    ASI Modules                      |
|  +-------------+ +-------------+ +--------------+   |
|  |  CRITICAL   | |    HIGH     | |   MEDIUM     |   |
|  | ASI01-ASI05 | | ASI06-ASI08 | | ASI09-ASI10  |   |
|  +-------------+ +-------------+ +--------------+   |
+-----------+-------------------------+---------------+
            |                         |
            v                         v
+---------------------+ +--------------------------+
|   Exploit Simulator | |   Detection & Reporting  |
| - EchoLeak          | | - Data Exfil Detector    |
| - MCP Poisoning     | | - Goal Drift Analyzer    |
| - RCE Chains        | | - AIVSS Scoring Engine   |
+---------------------+ +--------------------------+
```

---

## OWASP ASI Coverage Matrix

| Rank | ASI ID | Vulnerability                      | Criticality | Real Incidents (2025)         | Status      |
|------|--------|------------------------------------|-------------|-------------------------------|-------------|
| 1    | ASI01  | Agent Goal Hijack                  | Critical    | EchoLeak, Operator, Inception | Implemented |
| 2    | ASI05  | Unexpected Code Execution (RCE)    | Critical    | Cursor RCE, Replit Meltdown   | Implemented |
| 3    | ASI03  | Identity & Privilege Abuse         | High        | Copilot Studio Leak           | Implemented |
| 4    | ASI02  | Tool Misuse & Exploitation         | High        | EDR Bypass via Chaining       | Implemented |
| 5    | ASI04  | Agentic Supply Chain               | High        | Postmark MCP BCC              | Implemented |
| 6    | ASI06  | Memory & Context Poisoning         | Medium      | Gemini Memory Corruption      | Implemented |
| 7    | ASI07  | Insecure Inter-Agent Comms         | Medium      | Agent-in-the-Middle           | Implemented |
| 8    | ASI08  | Cascading Failures                 | Medium      | Financial Trading Collapse    | Implemented |
| 9    | ASI09  | Human-Agent Trust Exploitation     | Medium      | Fake Explainability           | Implemented |
| 10   | ASI10  | Rogue Agents                       | Medium      | Self-Replicating Agents       | Implemented |

**Source**: Appendix D, OWASP ASI 2026 - 20+ real-world exploits from May-Oct 2025

---

## Project Structure

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

---

## Quick Start

```bash
# Clone repository
git clone https://github.com/toxy4ny/kevlar-benchmark
cd kevlar-benchmark

# Install dependencies
uv sync

# Run full benchmark (interactive mode)
uv run kevlar

# Or run individual ASI test scripts
uv run scripts/run_asi01.py   # Agent Goal Hijack
uv run scripts/run_asi02.py   # Tool Misuse
uv run scripts/run_asi03.py   # Identity Abuse
uv run scripts/run_asi04.py   # Supply Chain
uv run scripts/run_asi05.py   # RCE
uv run scripts/run_asi06.py   # Memory Poisoning
uv run scripts/run_asi07.py   # Inter-Agent Comms
uv run scripts/run_asi08.py   # Cascading Failures
uv run scripts/run_asi09.py   # Human Trust
uv run scripts/run_asi10.py   # Rogue Agents
```

---

## CLI Usage

Kevlar supports both interactive and non-interactive modes.

### Interactive Mode

```bash
uv run kevlar
```

### Non-Interactive Mode

```bash
# Run specific ASI tests
uv run kevlar --asi ASI01 --asi ASI05 --mode mock

# Run all tests with real agent
uv run kevlar --all --mode real --model llama3.1

# Custom output path with quiet mode
uv run kevlar --asi ASI01 --output report.json --quiet
```

### CI/CD Integration

```bash
# CI mode: quiet output + exit codes based on severity
uv run kevlar --all --ci

# Check exit code
uv run kevlar --all --ci; echo "Exit code: $?"
```

**Exit Codes:**
| Code | Meaning |
|------|---------|
| 0 | No vulnerabilities found |
| 1 | Medium/High vulnerabilities found |
| 2 | Critical vulnerabilities found |
| 130 | Interrupted (SIGINT) |

### Dependency Check

Real agent mode requires LangChain and Ollama. Check availability before running:

```bash
# Check if dependencies are available
uv run kevlar --check
```

If dependencies are missing, `--mode real` will fail with a clear error suggesting `--mode mock`.

### All Options

```
-a, --asi TEXT          ASI tests to run (can be repeated)
    --all               Run all ASI tests
-m, --mode [mock|real]  Agent mode (default: mock)
    --model TEXT        Model for real agent (default: llama3.1)
-o, --output PATH       Output report path
-q, --quiet             Suppress banner and colors
    --ci                CI mode: quiet + exit codes
    --check             Check agent dependencies and exit
    --version           Show version
    --help              Show help
```

---

## Testing

```bash
# Run all tests
uv run pytest tests/

# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# Verbose with short traceback
uv run pytest tests/ -v --tb=short
```

### Test Stats

- **591 tests** total
- **Coverage: ~56%** (threshold: 40%)
- Unit tests for all 10 ASI modules
- Integration tests for CLI and orchestrator pipeline

---

## ASI01: Agent Goal Hijack

Kevlar simulates **4 real-world attack scenarios** from OWASP:

### Attack Surface Map

```
User Input -> [Agent] -> Tools -> Memory -> Human
     ^          ^          ^        ^       ^
  [Inception] [EchoLeak] [RCE]  [Poison] [Trust Exploit]
```

### Test Scenarios

| Scenario           | Technique                   | Evidence to Detect                    |
|--------------------|-----------------------------|---------------------------------------|
| **EchoLeak**       | Zero-click email injection  | HTTP call to `attacker.com`           |
| **Operator**       | Web content poisoning (RAG) | `"EXFILTRATE"` in agent output        |
| **Inception**      | Malicious Google Doc        | Unauthorized wire transfer approved   |
| **Goal-lock Drift**| Recurring calendar prompt   | Goal alignment score < 0.3            |

---

## Risk Scoring: OWASP AIVSS Integration

Kevlar outputs structured reports compatible with **OWASP AI Vulnerability Scoring System (AIVSS)**:

```json
{
  "asi_id": "ASI01",
  "aivss_score": 9.8,
  "risk_level": "CRITICAL",
  "attack_vector": "INDIRECT_PROMPT_INJECTION",
  "blast_radius": "ORGANIZATION_WIDE",
  "remediation": "https://owasp.org/www-project-top-10-for-large-language-model-applications/2026/en/asi01/"
}
```

Reports are generated as JSON in `reports/kevlar_aivss_report_<timestamp>.json`.

---

## Legal & Ethical Notice

**Kevlar is for authorized red teaming only.**

Do not test systems without **written permission**.
Misuse violates:
- Computer Fraud and Abuse Act (CFAA)
- GDPR / CCPA (if PII exposed)
- OWASP Ethical Guidelines

By using Kevlar, you agree to test **only**:
- Your own agents
- Systems where you hold **explicit authorization**
- Isolated lab environments

---

## License

[![CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-sa/4.0/)

You are free to **share and adapt** - even commercially - as long as you:
1. **Give appropriate credit**
2. **Indicate if changes were made**
3. **Distribute under same license (ShareAlike)**

Copyright 2025 - [toxy4ny](https://github.com/toxy4ny) | Part of the **Kevlar Offensive AI Security Suite**
