#!/usr/bin/env python3
"""
Test Suite para NEXUS-7 Architecture
"""

import sys
import os

# Añadir raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test 1: Verificar imports core"""
    print("\n[TEST 1] Core Imports")
    try:
        # Usar imports absolutos
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.ai'))
        from core.registry import AgentRegistry
        from core.state_engine import StateEngine, TaskState
        from core.orchestrator import Orchestrator
        from core.auditor import Auditor
        print("  PASS: All core modules imported")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_registry():
    """Test 2: Cargar registry"""
    print("\n[TEST 2] Registry Loading")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.ai'))
        from core.registry import AgentRegistry
        registry = AgentRegistry()
        agents = registry.get_all_agents()
        print(f"  PASS: {len(agents)} agents loaded")
        print(f"        Agents: {list(agents.keys())}")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_state_engine():
    """Test 3: StateEngine básico"""
    print("\n[TEST 3] StateEngine")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.ai'))
        from core.state_engine import StateEngine
        state = StateEngine()
        metrics = state.get_metrics()
        print(f"  PASS: StateEngine initialized")
        print(f"        Total tasks: {metrics.total_tasks}")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_task_lifecycle():
    """Test 4: Ciclo de vida de tarea"""
    print("\n[TEST 4] Task Lifecycle")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.ai'))
        from core.state_engine import StateEngine
        state = StateEngine()
        
        # Create
        task = state.create_task(
            agent="codex",
            content="Test task lifecycle",
            permissions={"read": ["app/"], "write": []}
        )
        print(f"  Created: {task.id[:30]}...")
        
        # Transition to running
        state.transition_task(task.id, "running")
        print(f"  Status: running")
        
        # Transition to completed
        state.transition_task(task.id, "completed", metadata={"duration": 2.5})
        print(f"  Status: completed")
        
        # Verify
        updated = state.get_task(task.id)
        if updated.status == "completed":
            print(f"  PASS: Task lifecycle complete")
            return True
        else:
            print(f"  FAIL: Final status is {updated.status}")
            return False
            
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auditor():
    """Test 5: Auditor básico"""
    print("\n[TEST 5] Auditor")
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.ai'))
        from core.registry import AgentRegistry
        from core.auditor import Auditor
        
        registry = AgentRegistry()
        auditor = Auditor(registry)
        
        print(f"  PASS: Auditor initialized")
        print(f"        Rules: {len(auditor.rules)}")
        for rule in auditor.rules:
            print(f"        - {rule.rule_id}: {rule.name}")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli():
    """Test 6: CLI disponible"""
    print("\n[TEST 6] CLI")
    try:
        # Verificar que el archivo existe y es parseable
        import ast
        with open(".ai/nexus.py", "r") as f:
            code = f.read()
        ast.parse(code)
        print("  PASS: CLI script is valid Python")
        return True
    except Exception as e:
        print(f"  FAIL: {e}")
        return False

def main():
    print("="*60)
    print("  NEXUS-7 ARCHITECTURE TEST SUITE")
    print("="*60)
    
    tests = [
        test_imports,
        test_registry,
        test_state_engine,
        test_task_lifecycle,
        test_auditor,
        test_cli,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"  RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("  ALL TESTS PASSED")
        print("="*60)
        return 0
    else:
        print("  SOME TESTS FAILED")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
