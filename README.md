# vibeCoding_setup

# 🚀 Zero-to-Hero Production Agentic AI: The Open-Source Blueprint
> **From Prompt Engineering to Enterprise-Grade Autonomous Systems**  
> *A battle-tested open-source reference guide for building, governing, and scaling AI Agents.*

---

## 📌 Executive Summary

Building production AI agents is not about writing longer prompts—it is about designing an **autonomous, governed software system**. 

A hobbyist project relies solely on prompts to ask the LLM to behave. A **mature enterprise system** enforces deterministic execution boundaries, on-demand capabilities, persistent memory, and complete operational observability.

```mermaid
flowchart TD
    User([User / Trigger]) --> Orchestrator[🤖 Agent Orchestrator]
    
    subgraph GovernancePlane["🪝 Governance Plane (Deterministic)"]
        PreHook["PreToolUse Hook\n(Safety Gate & RBAC)"]
        PostHook["PostToolUse Hook\n(Secret Redactor & Linter)"]
        StopHook["Stop Hook\n(Goal & Test Verifier)"]
    end

    subgraph CapabilityPlane["🧠 Capability & Context Plane"]
        Memory[("🧠 Memory Layer\n(Mem0 / pgvector)")]
        Skills["🧠 Skills Runbooks\n(Progressive Disclosure)"]
    end

    subgraph ExecutionPlane["🛠️ Execution Plane (MCP Standard)"]
        Tools["🛠️ Tools / MCP Servers\n(DB, GitHub, Filesystem, APIs)"]
    end

    subgraph ObservabilityPlane["📈 Observability Plane (Telemetry)"]
        Telemetry["📈 Tracing & Cost Metrics\n(Langfuse / OpenInference)"]
    end

    Orchestrator <--> Memory
    Orchestrator -->|Loads on-demand| Skills
    Orchestrator -->|Proposes Action| PreHook
    PreHook -->|Allowed| Tools
    Tools --> PostHook
    PostHook --> Orchestrator
    Orchestrator --> StopHook
    
    PreHook -.-> Telemetry
    PostHook -.-> Telemetry
    Tools -.-> Telemetry
```

---

## 🧭 The Core Paradigm: Skills vs. Hooks

The defining distinction between a prototype and a mature production system is the separation of **Capability** and **Governance**:

| Dimension | 🧠 Skills (Capability) | 🪝 Hooks (Governance) |
| :--- | :--- | :--- |
| **Question** | *"What can the agent do?"* | *"What must — and must not — the agent do?"* |
| **Role** | The **"How"** (Procedures, runbooks, workflows) | The **"Limits"** (Security boundaries, policy enforcement) |
| **Execution** | **Discretionary** (LLM chooses if/when to invoke) | **Deterministic** (System intercepts unconditionally) |
| **Format** | Markdown guides, documentation, example prompts | Shell scripts, Python validators, JSON-RPC interceptors |
| **Nature** | Generative, non-deterministic | Code-level gate, 100% deterministic (Pass / Deny / Ask) |
| **Origin** | Feature requests & capabilities | **Encoded Memory** (Past production incidents turned into code) |

> 💡 **"Hooks as Encoded Memory"**: Every time an agent makes a mistake in staging or production (e.g., executing a dangerous query or exposing an API token), **do not just add a sentence to your prompt**. Encode that lesson into a deterministic `PreToolUse` or `PostToolUse` Hook.

---

## 🏛️ The 6 Pillars of Production Agentic Systems

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRODUCTION AGENT STACK                            │
├──────────────────┬──────────────────┬──────────────────┬────────────────────┤
│ 🤖 Orchestration │ 🧠 Capabilities  │ 🪝 Governance    │ 🛠️ Execution       │
│ LangGraph        │ Modular Skills   │ Guardrails AI    │ MCP Protocol       │
│ CrewAI           │ Semantic Kernel  │ NeMo Guardrails  │ Docker Sandbox     │
├──────────────────┴──────────────────┼──────────────────┴────────────────────┤
│ 🧠 Memory & Context                 │ 📈 Observability & Evals              │
│ Mem0 / Letta / Cognee               │ Langfuse / Arize Phoenix / Promptfoo  │
└─────────────────────────────────────┴───────────────────────────────────────┘
```

---

## 1. 🤖 Multi-Agent Orchestration & Prompts

### The Orchestrator-Worker Architecture
Do not use a single massive agent with 50 tools. Split responsibilities into specialized agents operating with clear handoffs:
1. **Planner / Architect**: Breaks the problem into discrete, testable sub-tasks. Has zero direct write access to code.
2. **Coder / Executor**: Operates within a scoped directory. Executes tools permitted by policy.
3. **Reviewer / Verifier**: Evaluates code against quality and security criteria before human sign-off.

### Production System Prompt Engineering (Template)

Use structured tags (`<role>`, `<guidelines>`, `<constraints>`, `<output_format>`) to eliminate ambiguity:

```markdown
<system_instruction>
<role>
You are SeniorDevAgent, an autonomous software engineering agent specialized in TypeScript and Python microservices.
</role>

<operating_principles>
1. VERIFY BEFORE ASSUMING: Always inspect files and read existing tests before modifying code.
2. PROGRESSIVE DISCLOSURE: Refer to registered skills when performing domain-specific tasks.
3. MINIMAL SURGICAL EDITS: Never re-write entire files when localized diffs suffice.
4. HONEST UNCERTAINTY: If tool output or requirements are ambiguous, halt and solicit human feedback.
</operating_principles>

<mandatory_constraints>
- NEVER commit secrets, .env files, or API credentials.
- NEVER run raw destructive commands (`rm -rf`, `DROP TABLE`, `git reset --hard`).
- All tool executions are monitored by deterministic security hooks.
</mandatory_constraints>

<thought_process>
Before every tool invocation, formulate your internal reasoning inside:
<thinking>
- Goal: What exact sub-problem am I solving?
- Pre-conditions: Do I have all required inputs?
- Safety Check: Does this action comply with <mandatory_constraints>?
- Expected Outcome: What output indicates success?
</thinking>
</thought_process>
</system_instruction>
```

---

## 2. 🧠 Skills for Modular Capability

Skills are **on-demand packages** that prevent context window exhaustion. Only the skill name and description are visible to the agent initially; the full runbook is loaded only when triggered.

### Standardized Skill Directory Structure
```text
.agents/skills/database-migration/
├── SKILL.md                  # Main entry point with YAML frontmatter
├── scripts/                  # Deterministic helper scripts
│   ├── generate_diff.sh
│   └── run_dry_run.py
└── references/               # Bulky documentation loaded only if needed
    └── naming_conventions.md
```

### Example: `.agents/skills/database-migration/SKILL.md`
```markdown
---
name: database-migration
description: Use this skill whenever generating, testing, or applying relational database schema changes.
---

# Database Migration Runbook

## Safety Prerequisites
1. Ensure a local database dump exists before running migrations.
2. Dry-run the migration schema:
   `python3 ./scripts/run_dry_run.py`

## Execution Protocol
1. Verify column nullability constraints.
2. If adding an index on a table > 100k rows, use `CONCURRENTLY`.
3. Check the execution logs against [naming_conventions.md](./references/naming_conventions.md).
```

---

## 3. 🪝 Hooks for Deterministic Governance

Hooks intercept the agent execution loop at lifecycle checkpoints:
* `PreToolUse`: Gate dangerous tool arguments, block disallowed paths, require human authorization.
* `PostToolUse`: Auto-format code, validate schemas, sanitize sensitive leaks (PII/tokens).
* `Stop`: Block termination if tests fail or background tasks are unfinished.

### Configuration: `.agents/hooks.json`
```json
{
  "enterprise-governance": {
    "PreToolUse": [
      {
        "matcher": "run_command",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .agents/hooks/pre_tool_validator.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "write_to_file|replace_file_content",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .agents/hooks/post_tool_sanitizer.py"
          }
        ]
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "./.agents/hooks/verify_test_suite.sh"
      }
    ]
  }
}
```

### Production Pre-Tool Hook Implementation: `.agents/hooks/pre_tool_validator.py`
```python
#!/usr/bin/env python3
"""
PreToolUse Hook: Deterministic Guardrail Gate
Receives: JSON payload on stdin
Returns: JSON response on stdout {"decision": "allow" | "deny" | "ask"}
"""
import sys
import json
import re

DENY_PATTERNS = [
    r"rm\s+-rf\s+/",
    r":\(\)\{\s*:\|:&\s*\};:",  # Fork bomb
    r"mkfs",
    r"dd\s+if=",
    r"git\s+push\s+.*--force",
    r"DROP\s+DATABASE",
]

APPROVAL_REQUIRED_PATTERNS = [
    r"kubectl\s+delete",
    r"terraform\s+apply",
    r"npm\s+publish",
    r"git\s+reset\s+--hard",
]

def evaluate():
    try:
        data = json.load(sys.stdin)
    except Exception as e:
        # Fail safe
        print(json.dumps({"decision": "deny", "reason": f"Invalid JSON payload: {e}"}))
        return

    tool_call = data.get("toolCall", {})
    args = tool_call.get("args", {})
    cmd = args.get("CommandLine", "")

    # 1. Hard Block (Zero Trust)
    for pattern in DENY_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            print(json.dumps({
                "decision": "deny",
                "reason": f"SECURITY POLICY VIOLATION: Disallowed destructive pattern detected -> '{pattern}'"
            }))
            return

    # 2. Human-in-the-Loop Escalation
    for pattern in APPROVAL_REQUIRED_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            print(json.dumps({
                "decision": "ask",
                "reason": f"HIGH IMPACT ACTION: Command matches '{pattern}'. Operator confirmation required."
            }))
            return

    # 3. Allow execution
    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    evaluate()
```

---

## 4. 🛠️ Execution Plane: Model Context Protocol (MCP)

Never write bespoke, ad-hoc API wrappers for standard tools. Standardize all agent capabilities using **MCP**.

### Configuration: `.agents/mcp_config.json`
```json
{
  "mcpServers": {
    "postgres-dev": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost:5432/dev_db"],
      "env": {
        "READONLY": "true"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "filesystem-sandbox": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./src", "./tests"]
    }
  }
}
```

---

## 5. 🧠 Memory Architecture (Context Engineering)

Agents fail when their context window is cluttered with irrelevant history or lacks critical long-term lessons. Use a **tiered memory model**:

```mermaid
graph TD
    subgraph MemoryHierarchy["Tiered Context & Memory Architecture"]
        L1["L1: Working Context (Context Window)"]
        L2["L2: Hierarchical Rules (AGENTS.md & Directory Rules)"]
        L3["L3: Ephemeral Scratchpads (Artifacts & Step Logs)"]
        L4["L4: Long-Term Memory (Mem0 / Vector Graph Storage)"]
    end
```

### Implementing Long-Term Memory with Mem0
```python
from mem0 import Memory

# Initialize Mem0 with PostgreSQL pgvector / Qdrant
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": "localhost", "port": 6333}
    }
}
memory = Memory.from_config(config)

# Store past incident / user preference
memory.add(
    "Never run integration tests without setting TEST_ENV=isolated", 
    user_id="team_core", 
    metadata={"scope": "testing"}
)

# Retrieve relevant context before task execution
relevant_context = memory.search("How should I execute tests?", user_id="team_core")
```

---

## 6. 📈 Observability & Evaluation

In production, you cannot debug an agent by reading console prints. You need distributed tracing across all LLM steps and tool calls.

### The Open-Source Observability Stack
* **[Langfuse](https://github.com/langfuse/langfuse)**: 1-click self-hosted LLM tracing, latency breakdown, token costs, and prompt versioning.
* **[Arize Phoenix](https://github.com/Arize-ai/phoenix)**: OpenInference/OTel-native evaluation of hallucinations, tool calls, and retrieval relevance.
* **[Promptfoo](https://github.com/promptfoo/promptfoo)**: CI/CD test runner for LLM red-teaming, prompt regressions, and security checks.

---

## 📦 Top Open-Source Repositories & Boilerplates Catalog

| Pillar | Recommended Open-Source Project | GitHub Link | Why It Matters |
| :--- | :--- | :--- | :--- |
| **Full Stack Template** | **FastAPI LangGraph Template** | [`wassim249/...`](https://github.com/wassim249/fastapi-langgraph-agent-production-ready-template) | Complete starter with LangGraph, Mem0, pgvector, Langfuse, and Alembic. |
| **Clean Architecture** | **Clean LangGraph Agent** | [`eng-mostafa-alrahal/...`](https://github.com/eng-mostafa-alrahal/langgraph-agent-clean-architecture) | Enterprise Clean Architecture (Domain, UseCases, HITL, Docker). |
| **Governance / Hooks** | **Guardrails AI** | [`guardrails-ai/guardrails`](https://github.com/guardrails-ai/guardrails) | Structural validation, PII redaction, and strict output schemas. |
| **Governance / Hooks** | **NeMo Guardrails** | [`NVIDIA/NeMo-Guardrails`](https://github.com/NVIDIA/NeMo-Guardrails) | Programmable rails for conversational boundaries and safety policies. |
| **Tool Execution** | **MCP Servers Collection** | [`modelcontextprotocol/servers`](https://github.com/modelcontextprotocol/servers) | Official collection of ready-to-run MCP servers (DB, Git, Filesystem). |
| **Memory** | **Mem0** | [`mem0ai/mem0`](https://github.com/mem0ai/mem0) | The standard personalization and memory layer for autonomous agents. |
| **Memory** | **Letta (MemGPT)** | [`letta-ai/letta`](https://github.com/letta-ai/letta) | OS-level hierarchical memory virtualization for LLMs. |
| **Observability** | **Langfuse** | [`langfuse/langfuse`](https://github.com/langfuse/langfuse) | Production observability, evals, and audit tracing. |
| **Agent Testing** | **Promptfoo** | [`promptfoo/promptfoo`](https://github.com/promptfoo/promptfoo) | Automated red-teaming and prompt testing in CI/CD pipelines. |

---

## ⚡ Quickstart & Interactive Usage

### 1. Installation
```bash
# Clone the repository
git clone git@github.com:abdullokhmirzayev/vibeCoding_setup.git
cd vibeCoding_setup

# Create virtual environment and install dependencies
make setup
```

### 2. Run Test Suite
```bash
# Run all 17 unit tests (100% pass rate)
make test
```

### 3. Interactive CLI Console
```bash
# Inspect all registered skills with Progressive Disclosure
.venv/bin/python -m src.cli skills

# Test a command against deterministic PreToolUse governance hooks
.venv/bin/python -m src.cli check "rm -rf /"       # -> DENY
.venv/bin/python -m src.cli check "git reset --hard" # -> ASK (HITL)
.venv/bin/python -m src.cli check "git status"     # -> ALLOW

# Inspect dynamic XML-tagged prompt assembly
.venv/bin/python -m src.cli prompt

# Manage L4 persistent memory
.venv/bin/python -m src.cli memory
```

### 4. Launch FastAPI REST API Server
```bash
make run-api
# Open interactive Swagger Docs at http://localhost:8000/docs
```

Available API Endpoints:
* `GET  /health` - Server health and governance status
* `POST /api/v1/governance/check` - Real-time command verification
* `GET  /api/v1/skills` - List skills metadata
* `GET  /api/v1/skills/{name}` - Retrieve complete runbook and scripts
* `GET  /api/v1/memory` - Search long-term memory
* `POST /api/v1/memory` - Store new memory/preference
* `POST /api/v1/agent/run` - Autonomous governed agent execution loop

---

## 🏁 Zero-to-Hero 5-Phase Implementation Checklist

- [ ] **Phase 1: Foundation (Day 1)**
  - Establish `AGENTS.md` in repository root with project boundaries and coding standards.
  - Clone a production starter template (`fastapi-langgraph-agent-production-ready-template`).
  - Configure environment secret management (never hardcode keys).

- [ ] **Phase 2: Governance & Guardrails (Day 2)**
  - Configure `.agents/hooks.json` with `PreToolUse` security validators.
  - Set up command deny-lists and Human-in-the-Loop escalation rules.
  - Add `PostToolUse` secret sanitizers.

- [ ] **Phase 3: Execution via MCP (Day 3)**
  - Replace custom API scripts with standardized MCP servers in `.agents/mcp_config.json`.
  - Enforce read-only access on production data stores.

- [ ] **Phase 4: Modular Capabilities (Day 4)**
  - Identify recurring complex workflows (e.g., migrations, deployments, PR reviews).
  - Package each workflow into `.agents/skills/<name>/SKILL.md` with executable test scripts.

- [ ] **Phase 5: Telemetry & Memory (Day 5)**
  - Spin up local Langfuse via Docker Compose for complete trace observability.
  - Integrate Mem0 for persistent user/team context.
  - Add Promptfoo to GitHub Actions CI/CD to prevent prompt regressions.

---
*Created by the Open Source AI Engineering Community. Free to use, adapt, and distribute under the MIT License.*
