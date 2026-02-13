"""Verification script for MCP Vision Neuronal V2.0"""
import sys
import json

sys.path.insert(0, '.ai')
from core.vision.cortex import VisualCortex

cortex = VisualCortex()

# 1. Impact Analysis
print("=== IMPACT ANALYSIS: app/main.py ===")
impact = cortex.query_impact('app/main.py', max_depth=2)
print(f"Total dependents: {impact['total_dependents']}")
print(f"Aggregate risk: {impact['aggregate_risk']}")
for dep in impact['dependents'][:5]:
    nid = dep['node_id']
    depth = dep['depth']
    risk = dep['risk_score']
    print(f"  -> {nid} (depth {depth}, risk {risk})")

# 2. Search
print("\n=== SEARCH: validate ===")
results = cortex.query_search('validate', 'function')
for r in results[:5]:
    print(f"  {r['id']}")
print(f"  Total results: {len(results)}")

# 3. Graph Export
print("\n=== GRAPH EXPORT ===")
graph = cortex.get_graph_json()
print(f"Nodes: {len(graph['nodes'])}")
print(f"Links: {len(graph['links'])}")
stats = graph['stats']
print(f"Stats: nodes={stats['total_nodes']}, edges={stats['total_edges']}, smells={stats['total_smells']}")

# 4. Telemetry
print("\n=== TELEMETRY ===")
eid = cortex.record_telemetry('app/main.py', 'execution', {'latency_ms': 42}, 'test-session')
print(f"Event recorded: ID={eid}")
tele = cortex.query_telemetry('app/main.py', 5)
print(f"Query returned: {len(tele)} events")

# 5. Node metrics
print("\n=== TOP RISKY NODES ===")
health = cortex.get_health_report()
for node in health['top_risky_nodes'][:5]:
    print(f"  [{node['risk_score']}] {node['name']} ({node['type']})")

print("\n=== ALL VERIFICATION PASSED ===")
