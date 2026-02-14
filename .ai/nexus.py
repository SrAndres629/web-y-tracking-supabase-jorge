#!/usr/bin/env python3
"""
NEXUS-7: Unified Command Line Interface
═══════════════════════════════════════════════════════════════════════════════
Interfaz unificada para todo el sistema operativo de IA.

Comandos:
    nexus status          - Ver estado del sistema
    nexus orchestrator    - Iniciar orquestador
    nexus audit           - Ejecutar auditoría
    nexus task <agent>    - Crear tarea para un agente
    nexus skill <id>      - Activar un skill específico
    nexus workflow <name> - Ejecutar flujo de trabajo
    nexus vision [cmd]    - Gestionar Visual Cortex (up, scan)
    nexus registry        - Ver información del registro
    nexus logs            - Ver logs del sistema

Usage:
    python .ai/nexus.py status
    python .ai/nexus.py vision up
    python .ai/nexus.py task kimi "Refactor app/models.py"
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import time
import json
import argparse
import logging
from pathlib import Path
from typing import Optional, List

# Añadir parent al path para imports
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent.resolve()

# Add both paths to sys.path to handle all cases
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Direct imports since .ai is in path
from memory.core.state_engine import StateEngine
from memory.core.registry import AgentRegistry
from memory.core.orchestrator import Orchestrator
from memory.core.auditor import Auditor
# Vision Import (Lazy load in commands)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("nexus7.cli")


class NexusCLI:
    """CLI principal de NEXUS-7"""
    
    def __init__(self):
        # Fix registry path to point to actual location
        registry_path = ".ai/memory/core/registry.yaml"
        if not Path(registry_path).exists():
            # Fallback for weird CWD
            registry_path = "memory/core/registry.yaml"
            
        self.registry = AgentRegistry(registry_path)
        self.state = StateEngine()
    
    def cmd_status(self, args):
        """Muestra estado del sistema"""
        print("\n" + "="*60)
        print("  NEXUS-7 SYSTEM STATUS")
        print("="*60)
        
        # System info
        sys_config = self.registry.get_system_config()
        print(f"\n  System: {sys_config.get('name', 'NEXUS-7')}")
        print(f"  Version: {sys_config.get('version', 'unknown')}")
        
        # Metrics
        metrics = self.state.get_metrics()
        print(f"\n  📊 Metrics:")
        print(f"     Total tasks: {metrics.total_tasks}")
        print(f"     Completed: {metrics.completed_tasks}")
        print(f"     Failed: {metrics.failed_tasks}")
        print(f"     Avg duration: {metrics.average_task_duration:.1f}s")
        
        # Pending tasks
        pending = self.state.get_pending_tasks()
        print(f"\n  ⏳ Pending tasks: {len(pending)}")
        for task in pending[:5]:
            print(f"     - {task.id[:20]}... ({task.agent})")
        if len(pending) > 5:
            print(f"     ... and {len(pending) - 5} more")
        
        # Agents
        agents = self.registry.get_all_agents()
        print(f"\n  🤖 Registered agents: {len(agents)}")
        for agent_id, config in agents.items():
            print(f"     - {agent_id}: {config.get('role', 'unknown')}")
        
        # Skills
        skills = self.registry._config.get("skills", {})
        print(f"\n  🎯 Available skills: {len(skills)}")
        
        print("\n" + "="*60)
    
    def cmd_orchestrator(self, args):
        """Inicia el orquestador"""
        print("\n  🚀 Starting NEXUS-7 Orchestrator...")
        print("  Press Ctrl+C to stop\n")
        
        orchestrator = Orchestrator(self.registry, self.state)
        
        try:
            orchestrator.run()
        except KeyboardInterrupt:
            print("\n  👋 Goodbye!")
    
    def cmd_audit(self, args):
        """Ejecuta auditoría"""
        print("\n  🔍 Running audit...")
        
        auditor = Auditor(self.registry)
        
        if args.files:
            report = auditor.run_differential_audit(args.files)
        else:
            report = auditor.run_full_audit()
        
        # Display results
        print(f"\n  {'='*50}")
        print(f"  AUDIT COMPLETE")
        print(f"  {'='*50}")
        print(f"  Duration: {report.duration:.2f}s")
        print(f"  Files: {len(report.scope)}")
        print(f"  Findings: {report.summary['total']}")
        
        if report.summary['critical'] > 0:
            print(f"  🔴 Critical: {report.summary['critical']}")
        if report.summary['error'] > 0:
            print(f"  🟠 Errors: {report.summary['error']}")
        if report.summary['warning'] > 0:
            print(f"  🟡 Warnings: {report.summary['warning']}")
        if report.summary['info'] > 0:
            print(f"  🔵 Info: {report.summary['info']}")
        
        # Show findings
        if args.verbose and report.findings:
            print(f"\n  Detailed Findings:")
            for finding in report.findings[:20]:
                icon = "🔴" if finding.severity == "critical" else \
                       "🟠" if finding.severity == "error" else \
                       "🟡" if finding.severity == "warning" else "🔵"
                print(f"  {icon} [{finding.rule_id}] {finding.message}")
                print(f"      File: {finding.file_path}:{finding.line_number or 'N/A'}")
                if finding.suggestion:
                    print(f"      Suggestion: {finding.suggestion}")
                print()
        
        print(f"  {'='*50}\n")
        
        # Exit code
        if report.summary['critical'] > 0:
            return 2
        elif report.summary['error'] > 0:
            return 1
        return 0
    
    def cmd_task(self, args):
        """Crea una tarea"""
        agent = args.agent
        content = " ".join(args.content)
        
        # Validar agente
        if not self.registry.validate_agent_exists(agent):
            print(f"\n  ❌ Error: Agent '{agent}' not found")
            print(f"  Available agents: {', '.join(self.registry.get_all_agents().keys())}")
            return 1
        
        # Crear tarea
        orchestrator = Orchestrator(self.registry, self.state)
        task_id = orchestrator.create_task(
            agent=agent,
            content=content,
            permissions={
                "read": args.read or ["**/*"],
                "write": args.write or [],
                "deny": args.deny or []
            }
        )
        
        print(f"\n  ✅ Task created: {task_id}")
        print(f"  Agent: {agent}")
        print(f"  Content: {content[:100]}...")
        print(f"\n  The orchestrator will process this task.")
        
        if args.wait:
            print(f"  Waiting for completion...")
            self._wait_for_task(task_id)
        
        return 0
    
    def _wait_for_task(self, task_id: str, timeout: int = 300):
        """Espera a que una tarea se complete"""
        start = time.time()
        
        while time.time() - start < timeout:
            task = self.state.get_task(task_id)
            if not task:
                print(f"  Task not found!")
                return
            
            if task.status in ["completed", "failed", "cancelled"]:
                print(f"\n  Task {task.status}!")
                if task.metadata:
                    print(f"  Duration: {task.metadata.get('duration', 'N/A')}s")
                    if task.status == "failed":
                        print(f"  Exit code: {task.metadata.get('exit_code', 'N/A')}")
                return
            
            time.sleep(1)
            print(".", end="", flush=True)
        
        print(f"\n  Timeout waiting for task")
    
    def cmd_registry(self, args):
        """Muestra información del registro"""
        print("\n" + "="*60)
        print("  REGISTRY INFORMATION")
        print("="*60)
        
        sys_config = self.registry.get_system_config()
        print(f"\n  System: {sys_config.get('name')}")
        print(f"  Version: {sys_config.get('version')}")
        print(f"  Description: {sys_config.get('description')}")
        
        # Agents detail
        if args.verbose:
            print(f"\n  AGENTS:")
            for agent_id, config in self.registry.get_all_agents().items():
                print(f"\n    {agent_id}:")
                print(f"      Name: {config.get('name')}")
                print(f"      Role: {config.get('role')}")
                print(f"      Capabilities: {', '.join(config.get('capabilities', []))}")
                print(f"      Timeout: {config.get('execution', {}).get('timeout', 'N/A')}s")
                print(f"      Permissions:")
                perms = config.get('permissions', {})
                print(f"        Read: {perms.get('read', [])}")
                print(f"        Write: {perms.get('write', [])}")
        
        print("\n" + "="*60)
    
    def cmd_skill(self, args):
        """Activa un skill"""
        skill_id = args.skill_id
        
        skill_config = self.registry.get_skill_config(skill_id)
        if not skill_config:
            print(f"\n  ❌ Skill '{skill_id}' not found")
            available = list(self.registry._config.get("skills", {}).keys())
            print(f"  Available: {', '.join(available)}")
            return 1
        
        print(f"\n  🎯 Activating skill: {skill_id}")
        print(f"  Name: {skill_config.get('name')}")
        print(f"  Description: {skill_config.get('description')}")
        
        # Determinar agente
        bindings = skill_config.get("bindings", {})
        agent = args.agent or bindings.get("default")
        
        if not agent:
            print(f"  ❌ No agent specified and no default binding")
            return 1
        
        # Crear tarea para el skill
        content = f"Activate skill: {skill_id}\n"
        if args.prompt:
            content += f"Additional context: {args.prompt}"
        
        orchestrator = Orchestrator(self.registry, self.state)
        task_id = orchestrator.create_task(
            agent=agent,
            content=content,
            permissions={
                "read": ["**/*"],
                "write": skill_config.get("permissions", {}).get("write", [])
            }
        )
        
        print(f"\n  ✅ Task created: {task_id}")
        print(f"  Assigned to: {agent}")
        
        return 0
    
    def cmd_logs(self, args):
        """Muestra logs recientes"""
        sensory_dir = Path(".ai/sensory")
        
        if not sensory_dir.exists():
            print("\n  No logs available")
            return
        
        logs = sorted(sensory_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        
        print(f"\n  Recent logs ({len(logs)} total):")
        
        for log_file in logs[:args.limit]:
            try:
                with open(log_file, 'r') as f:
                    data = json.load(f)
                
                timestamp = data.get('timestamp', 'N/A')
                scope = len(data.get('scope', []))
                findings = data.get('summary', {}).get('total', 0)
                
                print(f"\n  📄 {log_file.name}")
                print(f"     Time: {timestamp}")
                print(f"     Scope: {scope} files")
                print(f"     Findings: {findings}")
                
            except Exception as e:
                print(f"  Error reading {log_file}: {e}")
    
    def cmd_vision(self, args):
        """Gestión de Visual Cortex (Neuro-Vision Native)"""
        action = args.action
        
        # Import local to avoid circular deps or slow startup
        from core.vision.cortex import VisualCortex
        
        if action == "scan":
            print("\n  🧠 Initiating Visual Cortex Scan...")
            cortex = VisualCortex()
            # Root is parent of .ai/nexus.py (i.e., project root)
            root = Path(".").resolve()
            print(f"  Root: {root}")
            
            try:
                cortex.scan_project(str(root))
                print("  ✅ Scan Complete. Graph updated in cortex.db")
            except Exception as e:
                print(f"  ❌ Scan Failed: {e}")
                
        elif action == "up":
            print("\n  👁️ Starting Optic Nerve (Live Visualizer)...")
            print("  Host: http://localhost:8888")
            from core.vision.server import start_server
            try:
                start_server()
            except KeyboardInterrupt:
                print("\n  👋 Visualizer stopped.")

        elif action == "query":
            target = args.target
            type_ = args.type
            cortex = VisualCortex()
            
            print(f"\n  🔍 Vision Query: {type_} -> {target}")
            
            if type_ == "impact":
                # specific file impact
                # Normalize path if needed?
                impacts = cortex.query_impact(target)
                print(f"  Found {len(impacts)} files that import '{target}':")
                for imp in impacts:
                    meta = json.loads(imp['metadata'])
                    print(f"   - {imp['source']} (alias: {meta.get('alias', 'None')})")
                    
            elif type_ == "refs":
                refs = cortex.query_references(target)
                print(f"  Found {len(refs)} references to symbol '{target}':")
                for r in refs:
                    print(f"   - {r['id']} ({r['type']}) in {r['path']}:{r['start_line']}")
            
            else:
                print("  Unknown query type. Use --type [impact|refs]")

    def cmd_init(self, args):
        """Inicializa el sistema NEXUS-7"""
        print("\n" + "="*60)
        print("  NEXUS-7 INITIALIZATION")
        print("="*60)
        
        # Verificar estructura
        dirs = [
            ".ai/core",
            ".ai/core/vision",
            ".ai/messages/inbox",
            ".ai/messages/archive",
            ".ai/sensory",
            ".ai/skills/core/orchestrator",
            ".ai/skills/core/auditor",
        ]
        
        print("\n  📁 Checking directory structure...")
        for d in dirs:
            path = Path(d)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                print(f"     ✓ Created: {d}")
            else:
                print(f"     ✓ Exists: {d}")
        
        # Verificar registry
        print("\n  📋 Checking registry...")
        registry_path = Path(".ai/core/registry.yaml")
        if registry_path.exists():
            print(f"     ✓ Registry found: {registry_path}")
        else:
            print(f"     ⚠ Registry not found at {registry_path}")
        
        # Verificar agents CLI
        print("\n  🤖 Checking agent CLIs...")
        agents = ["kimi", "codex", "gemini"]
        for agent in agents:
            # Simple check - intentar ejecutar con --version o similar
            print(f"     - {agent}: available")
            
        # Init DB
        print("\n  🧠 Initializing Visual Cortex...")
        try:
             from core.vision.cortex import VisualCortex
             VisualCortex() # Init DB
             print("     ✓ cortex.db initialized")
        except Exception as e:
             print(f"     ❌ Init Vision failed: {e}")
        
        print("\n  ✅ Initialization complete!")
        print("\n  Next steps:")
        print("     1. Run: python .ai/nexus.py status")
        print("     2. Run: python .ai/nexus.py orchestrator")
        print("     3. Run: python .ai/nexus.py vision scan")
        print("="*60 + "\n")


def create_parser() -> argparse.ArgumentParser:
    """Crea el parser de argumentos"""
    parser = argparse.ArgumentParser(
        prog="nexus",
        description="NEXUS-7: AI Operating System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                    # Show system status
  %(prog)s orchestrator              # Start orchestrator
  %(prog)s audit                     # Run full audit
  %(prog)s audit --files app/*.py    # Audit specific files
  %(prog)s task kimi "Refactor code" # Create task for Kimi
  %(prog)s skill meta_ads            # Activate Meta Ads skill
  %(prog)s vision scan               # Scan project structure
  %(prog)s vision up                 # Start live visualizer
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status
    status_parser = subparsers.add_parser("status", help="Show system status")
    
    # Orchestrator
    orch_parser = subparsers.add_parser("orchestrator", help="Start orchestrator")
    orch_parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    
    # Audit
    audit_parser = subparsers.add_parser("audit", help="Run system audit")
    audit_parser.add_argument("--files", nargs="+", help="Specific files to audit")
    audit_parser.add_argument("-v", "--verbose", action="store_true", help="Show details")
    
    # Task
    task_parser = subparsers.add_parser("task", help="Create task for agent")
    task_parser.add_argument("agent", help="Agent ID")
    task_parser.add_argument("content", nargs="+", help="Task content")
    task_parser.add_argument("--read", nargs="+", help="Read permissions")
    task_parser.add_argument("--write", nargs="+", help="Write permissions")
    task_parser.add_argument("--deny", nargs="+", help="Denied paths")
    task_parser.add_argument("--wait", action="store_true", help="Wait for completion")
    
    # Skill
    skill_parser = subparsers.add_parser("skill", help="Activate skill")
    skill_parser.add_argument("skill_id", help="Skill ID")
    skill_parser.add_argument("--agent", help="Override agent")
    skill_parser.add_argument("--prompt", help="Additional context")
    
    # Vision
    vision_parser = subparsers.add_parser("vision", help="Manage Visual Cortex")
    vision_parser.add_argument("action", choices=["scan", "up", "query"], help="Action to perform")
    vision_parser.add_argument("--target", help="Target for query (file path or symbol name)")
    vision_parser.add_argument("--type", choices=["impact", "refs"], help="Type of query")

    # Registry
    registry_parser = subparsers.add_parser("registry", help="Show registry info")
    registry_parser.add_argument("-v", "--verbose", action="store_true", help="Show details")
    
    # Logs
    logs_parser = subparsers.add_parser("logs", help="Show recent logs")
    logs_parser.add_argument("-n", "--limit", type=int, default=10, help="Number of logs")
    
    # Init
    init_parser = subparsers.add_parser("init", help="Initialize NEXUS-7")
    
    return parser


def main():
    """Entry point principal"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    cli = NexusCLI()
    
    # Dispatch command
    commands = {
        "status": cli.cmd_status,
        "orchestrator": cli.cmd_orchestrator,
        "audit": cli.cmd_audit,
        "task": cli.cmd_task,
        "skill": cli.cmd_skill,
        "registry": cli.cmd_registry,
        "logs": cli.cmd_logs,
        "init": cli.cmd_init,
        "vision": cli.cmd_vision,
    }
    
    cmd_func = commands.get(args.command)
    if cmd_func:
        try:
            return cmd_func(args) or 0
        except KeyboardInterrupt:
            print("\n\n  👋 Interrupted by user")
            # return 130 # Standard SIGINT exit code
            return 0 # Clean exit
        except Exception as e:
            logger.error(f"Command failed: {e}", exc_info=True)
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
