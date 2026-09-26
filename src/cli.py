import sys
import argparse
from src.core.config import settings
from src.governance.hook_engine import hook_engine
from src.skills.registry import skill_registry
from src.memory.manager import memory_manager
from src.agents.orchestrator import orchestrator

def print_header():
    print("=" * 65)
    print(" 🚀 VIBE CODING SETUP - Production Agentic AI Console")
    print("=" * 65)

def cmd_skills(args):
    print("\n🧠 Registered Skills (Progressive Disclosure):")
    skills = skill_registry.list_available_skills()
    if not skills:
        print("  (No skills found in .agents/skills/)")
        return

    for s in skills:
        print(f"\n• Name: {s.name}")
        print(f"  Description: {s.description}")
        print(f"  Path: {s.path}")
        print(f"  Scripts: {'Yes' if s.has_scripts else 'No'} | References: {'Yes' if s.has_references else 'No'}")

    if args.name:
        detail = skill_registry.get_skill_detail(args.name)
        if detail:
            print(f"\n--- [Full Content for {args.name}] ---")
            print(detail.content)
            if detail.scripts:
                print("\nExecutable Scripts:")
                for sc in detail.scripts:
                    print(f"  - {sc.name}")

def cmd_check(args):
    command = args.command
    print(f"\n🪝 Testing Governance Hook for command:\n  '{command}'\n")
    decision = hook_engine.run_pre_tool_hook("run_command", {"CommandLine": command})
    
    if decision.decision == "deny":
        print(f"❌ DECISION: DENY")
        print(f"   Reason: {decision.reason}")
    elif decision.decision in ["ask", "force_ask"]:
        print(f"⚠️  DECISION: ASK (Human Confirmation Required)")
        print(f"   Reason: {decision.reason}")
    else:
        print(f"✅ DECISION: ALLOW")
        print(f"   Reason: {decision.reason}")

def cmd_exec(args):
    command = args.command
    print(f"\n⚡ Executing command under governance: '{command}'")
    
    def confirm_cb(cmd, reason):
        print(f"\n⚠️  [APPROVAL REQUIRED] {reason}")
        ans = input(f"Proceed with '{cmd}'? (y/N): ").strip().lower()
        return ans in ["y", "yes"]

    res = orchestrator.execute_command_with_governance(command, confirm_callback=confirm_cb)
    if res.success:
        print("\n✅ Command completed successfully:")
        print(res.output)
    else:
        print("\n❌ Command failed or blocked:")
        print(res.error)

def cmd_prompt(args):
    print("\n📋 Assembled Production System Prompt:")
    prompt = orchestrator.prepare_context("sample query")
    print(prompt)

def cmd_memory(args):
    print("\n🧠 Tiered Memory Inspection:")
    rules = memory_manager.get_l2_rules()
    print(f"• L2 Hierarchical Rules ({len(rules)} chars):")
    if rules:
        print("  " + rules.strip().splitlines()[0] + " ...")
    else:
        print("  (Empty)")

    if args.add:
        mem_id = memory_manager.add_l4_memory(args.add, category="manual_entry")
        print(f"\n✅ Stored memory #{mem_id}: '{args.add}'")

    memories = memory_manager.query_l4_memory(limit=10)
    print(f"\n• L4 Long-Term Memories ({len(memories)} items):")
    for m in memories:
        print(f"  [{m['id']}] ({m['category']}) {m['content']} ({m['created_at'][:19]})")

def main():
    parser = argparse.ArgumentParser(description="VibeCoding Setup CLI")
    subparsers = parser.add_subparsers(dest="subcommand")

    # Skills subcommand
    p_skills = subparsers.add_parser("skills", help="List or inspect registered skills")
    p_skills.add_argument("--name", type=str, help="Skill name to view in detail")

    # Check subcommand
    p_check = subparsers.add_parser("check", help="Evaluate a command against governance hooks")
    p_check.add_argument("command", type=str, help="Command string to test")

    # Exec subcommand
    p_exec = subparsers.add_parser("exec", help="Execute command with full governance pipeline")
    p_exec.add_argument("command", type=str, help="Command string to run")

    # Prompt subcommand
    subparsers.add_parser("prompt", help="Display the dynamically generated system prompt")

    # Memory subcommand
    p_mem = subparsers.add_parser("memory", help="Inspect and manage L4 long-term memory")
    p_mem.add_argument("--add", type=str, help="Add a new memory string")

    args = parser.parse_args()

    print_header()
    if args.subcommand == "skills":
        cmd_skills(args)
    elif args.subcommand == "check":
        cmd_check(args)
    elif args.subcommand == "exec":
        cmd_exec(args)
    elif args.subcommand == "prompt":
        cmd_prompt(args)
    elif args.subcommand == "memory":
        cmd_memory(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
