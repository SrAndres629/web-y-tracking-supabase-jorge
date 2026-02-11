#!/usr/bin/env python3
import yaml
import sys

try:
    with open('.ai/core/registry.yaml', 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    print("OK: YAML is valid")
    print(f"  System: {data['system']['name']}")
    print(f"  Version: {data['system']['version']}")
    print(f"  Agents: {list(data['agents'].keys())}")
    print(f"  Skills: {list(data['skills'].keys())}")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
