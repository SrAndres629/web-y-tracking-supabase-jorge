"""Deep Code Inconsistency Audit - Using V2.0 Cortex"""
import sys
import json

sys.path.insert(0, '.ai')
from core.vision.cortex import VisualCortex
from core.vision.analyzers import CircularDependencyDetector

cortex = VisualCortex()

print("=" * 70)
print("  COGNITIVE VISUAL CORTEX V2.0 - DEEP INCONSISTENCY AUDIT")
print("=" * 70)

# 1. Health Report
health = cortex.get_health_report()
nc = health.get('node_counts', {})
sc = health.get('smell_counts', {})
print("\n[1] PROJECT HEALTH OVERVIEW")
print("    Health Score: %s/100" % health.get('health_score', 'N/A'))
print("    Node Counts: %s" % json.dumps(nc))
print("    Smell Counts: %s" % json.dumps(sc))

# 2. Top Risky Nodes
risky = health.get('top_risky_nodes', [])
print("\n[2] TOP 10 RISKY NODES")
for node in risky[:10]:
    name = node.get('name', 'unknown')
    ntype = node.get('type', '')
    risk = node.get('risk_score', 0)
    cc = node.get('cyclomatic_complexity', 0)
    cog = node.get('cognitive_complexity', 0)
    print("    [%5.1f] %-30s (%s) | CC=%s, Cog=%s" % (risk, name, ntype, cc, cog))

# 3. All Code Smells by severity
smells = cortex.query_smells()
print("\n[3] CODE SMELLS DETECTED: %d" % len(smells))
smells_by_severity = {}
for s in smells:
    sev = s.get('severity', 'info')
    if sev not in smells_by_severity:
        smells_by_severity[sev] = []
    smells_by_severity[sev].append(s)

for sev in ['critical', 'warning', 'info']:
    items = smells_by_severity.get(sev, [])
    if items:
        print("\n    [%s] (%d smells)" % (sev.upper(), len(items)))
        for s in items[:8]:
            smell_type = s.get('smell_type', '')
            node_id = s.get('node_id', '')
            details = s.get('details', '')
            print("      * %-25s -> %s" % (smell_type, node_id))
            print("        %s" % details)

# 4. Circular Dependencies
print("\n[4] CIRCULAR DEPENDENCY CHECK")
graph = cortex.get_graph_json()
detector = CircularDependencyDetector()
adj = {}
for link in graph.get('links', []):
    src = link.get('source', '')
    tgt = link.get('target', '')
    if link.get('type') == 'imports':
        if src not in adj:
            adj[src] = []
        adj[src].append(tgt)
cycles = detector.find_cycles(adj)
if cycles:
    print("    FOUND %d CIRCULAR DEPENDENCIES:" % len(cycles))
    for cycle in cycles[:5]:
        print("      -> %s" % ' -> '.join(cycle))
else:
    print("    No circular dependencies found OK")

# 5. Ghost References
print("\n[5] GHOST REFERENCES (broken imports)")
node_ids = set(n.get('id', '') for n in graph.get('nodes', []))
ghost_refs = []
for link in graph.get('links', []):
    if link.get('type') == 'imports' and link.get('target') not in node_ids:
        ghost_refs.append(link)

if ghost_refs:
    internal = {}
    for g in ghost_refs:
        src = g.get('source', 'unknown')
        tgt = g.get('target', '')
        if 'app' in tgt.lower() or 'core' in tgt.lower() or '.ai' in tgt.lower():
            if src not in internal:
                internal[src] = []
            internal[src].append(tgt)

    if internal:
        total_broken = sum(len(v) for v in internal.values())
        print("    WARNING: %d POTENTIALLY BROKEN INTERNAL IMPORTS:" % total_broken)
        for src, targets in internal.items():
            for t in targets:
                print("      %s -> %s (NOT FOUND)" % (src, t))
    else:
        print("    All internal imports resolve correctly OK")
        print("    (%d external lib imports not in graph, normal)" % len(ghost_refs))
else:
    print("    All imports resolve OK")

# 6. Duplicate Function Definitions
print("\n[6] DUPLICATE FUNCTION NAMES (potential shadowing)")
func_names = {}
for node in graph.get('nodes', []):
    if node.get('type') == 'function':
        name = node.get('label', '')
        nid = node.get('id', '')
        if name.startswith('__') and name.endswith('__'):
            continue
        if name not in func_names:
            func_names[name] = []
        func_names[name].append(nid)

duplicates = {k: v for k, v in func_names.items() if len(v) > 1}
significant_dups = {}
for name, locations in duplicates.items():
    real = [loc for loc in locations if 'refactor_backup' not in loc and 'tests' not in loc]
    if len(real) > 1:
        significant_dups[name] = real

if significant_dups:
    print("    %d functions defined in multiple locations:" % len(significant_dups))
    for name, locs in sorted(significant_dups.items()):
        print("    * %s:" % name)
        for loc in locs:
            print("        - %s" % loc)
else:
    print("    No significant duplicates found OK")

# 7. Orphan files
print("\n[7] ORPHAN FILES (no connections)")
orphan_count = 0
for fn in graph.get('nodes', []):
    if fn.get('type') != 'file':
        continue
    fid = fn.get('id', '')
    in_deg = fn.get('metrics', {}).get('in_degree', 0)
    out_deg = fn.get('metrics', {}).get('out_degree', 0)
    if in_deg == 0 and out_deg == 0 and 'test' not in fid.lower() and 'refactor_backup' not in fid:
        print("    * %s -- no imports and no dependents" % fid)
        orphan_count += 1
if orphan_count == 0:
    print("    No orphan files found OK")

# 8. Impact Analysis on Critical Files
print("\n[8] IMPACT ANALYSIS - CRITICAL FILES")
critical_files = ['app/config.py', 'app/database.py', 'app/tracking.py', 'app/meta_capi.py']
for cf in critical_files:
    impact = cortex.query_impact(cf, max_depth=2)
    deps = impact.get('total_dependents', 0)
    risk = impact.get('aggregate_risk', 0)
    print("    %s: %d dependents, aggregate risk %.1f" % (cf, deps, risk))

print("\n" + "=" * 70)
print("  AUDIT COMPLETE")
print("=" * 70)
