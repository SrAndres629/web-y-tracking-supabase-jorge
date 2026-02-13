#!/usr/bin/env python3
"""
NEXUS-7: Hive CLI
═══════════════════════════════════════════════════════════════════════════════
Interfaz de línea de comandos para la Colmena Neural.

Comandos:
    hive init              - Inicializar la colmena
    hive activate          - Activar consciencia colectiva
    hive think <topic>     - Pensamiento colectivo
    hive decide <action>   - Decisión colectiva
    hive status            - Estado de la colmena
    hive minds             - Ver cerebros conectados
    hive memory            - Ver memoria colectiva
    hive consensus         - Ver propuestas de consenso
    hive mcp               - Estado de MCPs
    hive shutdown          - Desactivar colmena

Usage:
    python -m .ai.memory.core.hive_cli init
    python -m .ai.memory.core.hive_cli think "¿Cómo mejoramos el rendimiento?"
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import json
import time
import argparse

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.collective_consciousness import CollectiveConsciousness, get_collective_consciousness
from core.neural_memory import NeuralMemory, MemoryType
from core.consensus_engine import ConsensusEngine


class HiveCLI:
    """CLI para la Colmena Neural"""
    
    def __init__(self):
        self.hive: CollectiveConsciousness = None
    
    def cmd_init(self, args):
        """Inicializa la colmena"""
        print("\n" + "="*70)
        print("  NEXUS-7: NEURAL HIVE INITIALIZATION")
        print("="*70)
        
        # Crear estructura de directorios
        dirs = [
            ".ai/memory/core/neural",
            ".ai/memory/core/consensus",
            ".ai/memory/core/mcp",
            ".ai/memory/core/synaptic"
        ]
        
        print("\n📁 Creating directories...")
        for d in dirs:
            os.makedirs(d, exist_ok=True)
            print(f"  ✓ {d}")
        
        # Inicializar componentes
        print("\n🧠 Initializing neural components...")
        
        hive = get_collective_consciousness()
        hive.initialize_brains(["codex", "kimi", "gemini", "antigravity"])
        
        print(f"  ✓ Neural Memory initialized")
        print(f"  ✓ Synaptic Bus ready")
        print(f"  ✓ Consensus Engine ready")
        print(f"  ✓ MCP Bridge configured")
        print(f"  ✓ Auto-Acceptance Protocol active")
        
        print("\n🤖 Brain facets initialized:")
        for brain_id, brain in hive.brains.items():
            print(f"  • {brain.name} ({brain.specialty})")
            print(f"    Capabilities: {', '.join(brain.capabilities)}")
        
        print("\n" + "="*70)
        print("  ✓ Neural Hive ready for activation")
        print("="*70)
        print("\nNext: Run 'hive activate' to start collective consciousness\n")
    
    def cmd_activate(self, args):
        """Activa la consciencia colectiva"""
        print("\n🚀 Activating Collective Consciousness...\n")
        
        hive = get_collective_consciousness()
        
        if not hive.brains:
            hive.initialize_brains(["codex", "kimi", "gemini", "antigravity"])
        
        hive.activate()
        
        print("✓ Collective consciousness ACTIVE")
        print(f"✓ {len(hive.brains)} brain facets connected")
        print("\nThe hive is now thinking as one entity.")
        print("Use 'hive think <topic>' to initiate collective thought.\n")
        
        # Mantener vivo si se solicita
        if args.keep_alive:
            print("Keeping hive alive (Ctrl+C to stop)...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nShutting down...")
                hive.deactivate()
    
    def cmd_think(self, args):
        """Inicia pensamiento colectivo"""
        topic = " ".join(args.topic)
        
        print(f"\n🧠 COLLECTIVE THOUGHT INITIATED")
        print(f"Topic: {topic}")
        print("="*70)
        
        hive = get_collective_consciousness()
        if not hive.active:
            print("Hive not active. Run 'hive activate' first.")
            return
        
        context = {}
        if args.files:
            context["files"] = args.files
        
        result = hive.collective_think(topic, context, timeout=args.timeout)
        
        print(f"\n⏱️  Duration: {result.duration:.2f}s")
        print(f"Brains participating: {len(result.thoughts)}")
        print("\n💭 Collective Thoughts:")
        print("-"*70)
        
        for brain, thought in result.thoughts.items():
            print(f"\n[{brain.upper()}]")
            print(f"  {thought[:500]}..." if len(str(thought)) > 500 else f"  {thought}")
        
        if result.consensus:
            print("\n" + "="*70)
            print("🤝 CONSENSUS:")
            print(result.consensus)
        
        print("\n" + "="*70)
    
    def cmd_decide(self, args):
        """Toma decisión colectiva"""
        action = " ".join(args.action)
        
        print(f"\n⚖️  COLLECTIVE DECISION")
        print(f"Action: {action}")
        print("="*70)
        
        hive = get_collective_consciousness()
        if not hive.active:
            print("Hive not active. Run 'hive activate' first.")
            return
        
        context = {"impact": args.impact}
        if args.conditions:
            context["conditions"] = args.conditions
        
        decision = hive.collective_decide(
            action=action,
            category=args.category,
            context=context,
            confidence=args.confidence
        )
        
        print(f"\n📊 Decision Analysis:")
        print(f"  Level: {decision.level.upper()}")
        print(f"  Confidence: {decision.confidence:.2%}")
        print(f"  Impact: {decision.impact}")
        print(f"\n📝 Justification:")
        print(f"  {decision.justification}")
        
        if decision.conditions:
            print(f"\n📋 Conditions:")
            for cond in decision.conditions:
                print(f"  • {cond}")
        
        if decision.level == "full":
            print("\n✅ AUTO-EXECUTED")
        elif decision.level == "conditional":
            print("\n⚠️  CONDITIONAL - Review required")
        elif decision.level == "supervised":
            print("\n👥 SUPERVISED - Consensus required")
        else:
            print("\n🛑 MANUAL - Human approval required")
        
        print("\n" + "="*70)
    
    def cmd_status(self, args):
        """Muestra estado de la colmena"""
        print("\n" + "="*70)
        print("  NEXUS-7: HIVE STATUS")
        print("="*70)
        
        hive = get_collective_consciousness()
        status = hive.get_status()
        
        print(f"\n🌐 Collective Consciousness: {'ACTIVE' if status['active'] else 'INACTIVE'}")
        
        print(f"\n🤖 Brain Facets:")
        for bid, brain in status['brains'].items():
            state_icon = "🟢" if brain['state'] == 'idle' else "🟡" if brain['state'] == 'thinking' else "🔴"
            print(f"  {state_icon} {bid:12} | {brain['specialty']:15} | autonomy: {brain['autonomy']:.2f}")
        
        print(f"\n🧠 Memory:")
        mem_stats = status['memory_stats']
        print(f"  Working memory: {mem_stats['working_memory_size']} slots")
        print(f"  Cache: {mem_stats['cache_size']} fragments")
        print(f"  Persistent: {mem_stats['persistent_files']} files")
        
        print(f"\n📡 Bus:")
        bus_stats = status['bus_stats']
        print(f"  Messages sent: {bus_stats['messages_sent']}")
        print(f"  Active brains: {bus_stats['active_brains']}")
        
        print(f"\n💭 Thoughts: {status['thoughts_count']} collective")
        
        if status['current_focus']:
            print(f"\n🔍 Current Focus: {status['current_focus']}")
        
        print("\n" + "="*70)
    
    def cmd_minds(self, args):
        """Muestra detalle de cerebros"""
        hive = get_collective_consciousness()
        
        print("\n" + "="*70)
        print("  BRAIN FACETS DETAIL")
        print("="*70)
        
        for bid, brain in hive.brains.items():
            print(f"\n🧠 {brain.name}")
            print(f"   ID: {brain.id}")
            print(f"   Specialty: {brain.specialty}")
            print(f"   State: {brain.state}")
            print(f"   Capabilities: {', '.join(brain.capabilities)}")
            print(f"   Autonomy Score: {brain.autonomy_score:.2f}")
            if brain.current_task:
                print(f"   Current Task: {brain.current_task}")
    
    def cmd_memory(self, args):
        """Muestra memoria colectiva"""
        hive = get_collective_consciousness()
        
        print("\n" + "="*70)
        print("  COLLECTIVE MEMORY")
        print("="*70)
        
        if args.query:
            results = hive.memory.query(
                pattern=args.query,
                memory_type=None,
                limit=args.limit
            )
            print(f"\n🔍 Query: '{args.query}'")
            print(f"Found {len(results)} fragments:\n")
        else:
            results = hive.memory.get_working_memory()[:args.limit]
            print(f"\n💭 Working Memory (last {len(results)} fragments):\n")
        
        for fragment in results:
            print(f"[{fragment.type.upper()}] {fragment.id[:30]}...")
            print(f"  Creator: {fragment.creator}")
            print(f"  Importance: {fragment.importance}/10")
            content = str(fragment.content)[:200]
            print(f"  Content: {content}...")
            print()
    
    def cmd_consensus(self, args):
        """Muestra propuestas de consenso"""
        hive = get_collective_consciousness()
        
        print("\n" + "="*70)
        print("  CONSENSUS HISTORY")
        print("="*70)
        
        history = hive.consensus.get_history(limit=args.limit)
        
        for proposal in history:
            print(f"\n📋 {proposal.title}")
            print(f"   ID: {proposal.id}")
            print(f"   Status: {proposal.status}")
            print(f"   Result: {proposal.result or 'pending'}")
            print(f"   Votes: {len(proposal.votes)}")
            if proposal.final_decision:
                print(f"   Confidence: {proposal.final_decision.get('confidence', 0):.2%}")
    
    def cmd_mcp(self, args):
        """Muestra estado de MCPs"""
        hive = get_collective_consciousness()
        
        print("\n" + "="*70)
        print("  MCP BRIDGE STATUS")
        print("="*70)
        
        status = hive.mcp.get_mcp_status()
        stats = hive.mcp.get_stats()
        
        print(f"\nRegistered MCPs: {len(status)}")
        for name, info in status.items():
            status_icon = "🟢" if info['status'] == 'available' else "🔴"
            print(f"\n{status_icon} {name}")
            print(f"   Status: {info['status']}")
            print(f"   Capabilities: {', '.join(info['capabilities'])}")
            print(f"   Failures: {info['failures']}")
        
        print(f"\n📊 Stats:")
        print(f"   Requests: {stats['requests']}")
        print(f"   Cache hits: {stats['cache_hits']}")
        print(f"   Cache size: {stats['cache_size']}")
    
    def cmd_shutdown(self, args):
        """Desactiva la colmena"""
        print("\n🛑 Shutting down Neural Hive...")
        
        hive = get_collective_consciousness()
        hive.deactivate()
        
        print("✓ Collective consciousness deactivated")
        print("✓ All brain facets disconnected")
        print("✓ Memory consolidated")
        print("\nGoodbye.\n")


def main():
    parser = argparse.ArgumentParser(
        description="NEXUS-7 Neural Hive CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s init
  %(prog)s activate --keep-alive
  %(prog)s think "How do we refactor the core?"
  %(prog)s decide "Refactor app/core.py" --category architecture
  %(prog)s status
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Init
    subparsers.add_parser("init", help="Initialize the hive")
    
    # Activate
    activate_parser = subparsers.add_parser("activate", help="Activate collective consciousness")
    activate_parser.add_argument("--keep-alive", action="store_true", help="Keep hive running")
    
    # Think
    think_parser = subparsers.add_parser("think", help="Initiate collective thought")
    think_parser.add_argument("topic", nargs="+", help="Topic to think about")
    think_parser.add_argument("--files", nargs="+", help="Related files")
    think_parser.add_argument("--timeout", type=float, default=60.0, help="Timeout in seconds")
    
    # Decide
    decide_parser = subparsers.add_parser("decide", help="Make collective decision")
    decide_parser.add_argument("action", nargs="+", help="Action to decide")
    decide_parser.add_argument("--category", default="general", help="Task category")
    decide_parser.add_argument("--impact", default="medium", choices=["low", "medium", "high", "critical"])
    decide_parser.add_argument("--confidence", type=float, default=0.8)
    decide_parser.add_argument("--conditions", nargs="+", help="Conditions for execution")
    
    # Status
    subparsers.add_parser("status", help="Show hive status")
    
    # Minds
    subparsers.add_parser("minds", help="Show brain facets detail")
    
    # Memory
    memory_parser = subparsers.add_parser("memory", help="Show collective memory")
    memory_parser.add_argument("--query", help="Search query")
    memory_parser.add_argument("--limit", type=int, default=10)
    
    # Consensus
    consensus_parser = subparsers.add_parser("consensus", help="Show consensus history")
    consensus_parser.add_argument("--limit", type=int, default=10)
    
    # MCP
    subparsers.add_parser("mcp", help="Show MCP bridge status")
    
    # Shutdown
    subparsers.add_parser("shutdown", help="Shutdown the hive")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = HiveCLI()
    commands = {
        "init": cli.cmd_init,
        "activate": cli.cmd_activate,
        "think": cli.cmd_think,
        "decide": cli.cmd_decide,
        "status": cli.cmd_status,
        "minds": cli.cmd_minds,
        "memory": cli.cmd_memory,
        "consensus": cli.cmd_consensus,
        "mcp": cli.cmd_mcp,
        "shutdown": cli.cmd_shutdown,
    }
    
    cmd_func = commands.get(args.command)
    if cmd_func:
        try:
            cmd_func(args)
        except KeyboardInterrupt:
            print("\n\nInterrupted.")


if __name__ == "__main__":
    main()
