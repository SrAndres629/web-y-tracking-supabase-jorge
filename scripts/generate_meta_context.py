#!/usr/bin/env python3
"""
META_CONTEXT.json Generator — Persistent Memory for Antigravity AI Agent.

Scans the project and generates a structured context file that serves as
the AI agent's persistent memory between conversations. Records:
- Architecture decisions
- Technical debt
- CTA/conversion points
- Design system tokens
- Deployment state
- Business context

Usage:
    python scripts/generate_meta_context.py
"""

import json
import os
import re
import glob
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "META_CONTEXT.json"


def scan_templates() -> dict:
    """Scan HTML templates and extract CTA points, sections, and structure."""
    templates_dir = PROJECT_ROOT / "api" / "templates"
    sections = []
    cta_points = []
    component_files = []

    for html_file in sorted(templates_dir.rglob("*.html")):
        rel_path = str(html_file.relative_to(PROJECT_ROOT))
        content = html_file.read_text(encoding="utf-8", errors="ignore")

        # Find handleConversion calls
        for match in re.finditer(r"handleConversion\(['\"](.+?)['\"]\)", content):
            cta_points.append({
                "label": match.group(1),
                "file": rel_path,
                "line": content[:match.start()].count("\n") + 1,
            })

        # Categorize files
        if "sections/" in rel_path:
            section_id = re.search(r'id="([^"]+)"', content)
            sections.append({
                "file": rel_path,
                "section_id": section_id.group(1) if section_id else None,
            })
        elif "components/" in rel_path:
            component_files.append(rel_path)

    return {
        "sections": sections,
        "components": component_files,
        "cta_points": cta_points,
        "total_ctas": len(cta_points),
    }


def scan_css_architecture() -> dict:
    """Scan CSS files and detect design system tokens and potential duplication."""
    input_css = PROJECT_ROOT / "static" / "src" / "input.css"
    atoms_dir = PROJECT_ROOT / "static" / "atoms"
    tokens_dir = PROJECT_ROOT / "static" / "design-system" / "tokens"

    atom_files = sorted(str(p.relative_to(PROJECT_ROOT)) for p in atoms_dir.rglob("*.css")) if atoms_dir.exists() else []
    token_files = sorted(str(p.relative_to(PROJECT_ROOT)) for p in tokens_dir.rglob("*.css")) if tokens_dir.exists() else []

    # Extract class names from input.css @layer components
    layer_classes = []
    if input_css.exists():
        content = input_css.read_text(encoding="utf-8", errors="ignore")
        layer_classes = re.findall(r"\.([\w-]+)\s*\{", content)

    return {
        "entry_point": "static/src/input.css",
        "output": "static/dist/css/app.min.css",
        "atom_files": atom_files,
        "token_files": token_files,
        "layer_component_classes": layer_classes,
        "potential_duplicates_note": "Classes defined in both atoms/ and input.css @layer need dedup audit",
    }


def scan_tailwind_config() -> dict:
    """Extract design tokens from tailwind.config.js."""
    config_path = PROJECT_ROOT / "tailwind.config.js"
    if not config_path.exists():
        return {}

    content = config_path.read_text(encoding="utf-8", errors="ignore")

    colors = dict(re.findall(r"'(luxury-[\w-]+)':\s*'(#[0-9a-fA-F]+)'", content))
    fonts = dict(re.findall(r"(\w+):\s*\['([^']+)'", content))

    return {
        "colors": colors,
        "fonts": fonts,
        "file": "tailwind.config.js",
    }


def scan_env_vars() -> list:
    """List environment variable keys (not values) from .env files."""
    env_keys = set()
    for env_file in [".env", ".env.production"]:
        env_path = PROJECT_ROOT / env_file
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key = line.split("=", 1)[0].strip()
                    env_keys.add(key)
    return sorted(env_keys)


def scan_tech_debt() -> list:
    """Identify known technical debt items."""
    debt = []

    # Check for text-luxury-gray misuse (should be fully fixed now)
    templates_dir = PROJECT_ROOT / "api" / "templates"
    for html_file in templates_dir.rglob("*.html"):
        content = html_file.read_text(encoding="utf-8", errors="ignore")
        if "text-luxury-gray" in content:
            debt.append({
                "type": "wcag_contrast",
                "severity": "critical",
                "file": str(html_file.relative_to(PROJECT_ROOT)),
                "description": "text-luxury-gray (#1a1a1a) used as text color on dark bg — invisible",
            })

    # Check for fixed width overflow risks
    for html_file in templates_dir.rglob("*.html"):
        content = html_file.read_text(encoding="utf-8", errors="ignore")
        fixed_widths = re.findall(r'w-\[(\d+)px\]', content)
        for w in fixed_widths:
            if int(w) > 400:
                debt.append({
                    "type": "overflow_x",
                    "severity": "high",
                    "file": str(html_file.relative_to(PROJECT_ROOT)),
                    "description": f"Fixed width w-[{w}px] may overflow mobile viewport",
                })

    return debt


def build_meta_context() -> dict:
    """Build the complete META_CONTEXT."""
    return {
        "_meta": {
            "version": "2.6",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator": "scripts/generate_meta_context.py",
            "purpose": "Persistent memory for Antigravity AI agent",
        },
        "business": {
            "name": "Jorge Aguirre Flores",
            "domain": "jorgeaguirreflores.com",
            "industry": "Maquillaje Permanente / Microblading",
            "location": "Santa Cruz, Bolivia",
            "target_audience": "Mujeres 25-55, mobile-first (90% tráfico desde Meta Ads)",
            "brand_values": ["Lujo", "Profesionalismo", "Confianza", "30+ años experiencia"],
        },
        "architecture": {
            "stack": "Python/Flask + Jinja2 + Tailwind CSS + Supabase + Meta CAPI",
            "hosting": "Vercel (Serverless Python)",
            "cdn": "Cloudflare",
            "pattern": "Clean Architecture (app/domain, app/application, app/infrastructure, app/interfaces)",
            "entry_point": "api/index.py → main.py",
        },
        "templates": scan_templates(),
        "css_architecture": scan_css_architecture(),
        "design_tokens": scan_tailwind_config(),
        "env_vars_keys": scan_env_vars(),
        "technical_debt": scan_tech_debt(),
        "decisions": [
            {
                "date": "2026-02-18",
                "decision": "app.min.css loaded render-blocking (not async) to eliminate FOUC",
                "rationale": "47KB is acceptable tradeoff vs FOUC on mobile",
            },
            {
                "date": "2026-02-18",
                "decision": "Replaced text-luxury-gray with text-gray-300 for body text",
                "rationale": "luxury-gray (#1a1a1a) is a surface color, not readable as text on #0a0a0a bg",
            },
            {
                "date": "2026-02-18",
                "decision": "Mobile H1 reduced from text-5xl (48px) to text-4xl (36px)",
                "rationale": "Golden ratio typography scale for 390px viewport",
            },
            {
                "date": "2026-02-18",
                "decision": "Fixed-width glow elements changed to vw-relative with max-w caps",
                "rationale": "Prevent overflow-X on mobile viewports < 400px",
            },
            {
                "date": "2026-02-18",
                "decision": "CTA touch targets increased to py-4 (≥44px height)",
                "rationale": "Fitts' law compliance for mobile thumb interaction",
            },
        ],
    }


if __name__ == "__main__":
    context = build_meta_context()
    OUTPUT_PATH.write_text(json.dumps(context, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ META_CONTEXT.json generated at {OUTPUT_PATH}")
    print(f"   Template sections: {len(context['templates']['sections'])}")
    print(f"   CTA points: {context['templates']['total_ctas']}")
    print(f"   Tech debt items: {len(context['technical_debt'])}")
    print(f"   Architecture decisions: {len(context['decisions'])}")
