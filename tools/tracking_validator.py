#!/usr/bin/env python3
"""
Tracking Validator — Validates CTA → handleConversion() integrity.

Scans all HTML templates to ensure:
1. Every CTA button/link calls handleConversion() with a unique label
2. No orphaned CTAs exist without tracking
3. Labels follow naming convention

Usage:
    python tools/tracking_validator.py
"""

import re
import sys
from pathlib import Path
from collections import Counter


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "api" / "templates"


def scan_ctas() -> dict:
    """Scan all templates for CTA elements and their tracking status."""
    results = {
        "tracked_ctas": [],
        "untracked_ctas": [],
        "duplicate_labels": [],
        "total_buttons": 0,
        "total_links_with_onclick": 0,
    }

    label_counter = Counter()

    for html_file in sorted(TEMPLATES_DIR.rglob("*.html")):
        content = html_file.read_text(encoding="utf-8", errors="ignore")
        rel_path = str(html_file.relative_to(PROJECT_ROOT))

        # Find all handleConversion calls
        for match in re.finditer(r"handleConversion\(['\"](.+?)['\"]\)", content):
            label = match.group(1)
            line = content[:match.start()].count("\n") + 1
            results["tracked_ctas"].append({
                "label": label,
                "file": rel_path,
                "line": line,
            })
            label_counter[label] += 1

        # Find buttons without handleConversion
        for match in re.finditer(r"<button[^>]*>", content):
            tag = match.group(0)
            if "handleConversion" not in tag and "type=\"submit\"" not in tag:
                # Check if it's a UI-only button (menu toggle, etc)
                if any(x in tag for x in ["toggleMobileMenu", "closeMobileMenu", "accordion", "x-on"]):
                    continue
                line = content[:match.start()].count("\n") + 1
                results["untracked_ctas"].append({
                    "element": "button",
                    "file": rel_path,
                    "line": line,
                    "snippet": tag[:100],
                })

        # Find links with onclick but without handleConversion
        for match in re.finditer(r"<a[^>]*onclick[^>]*>", content):
            tag = match.group(0)
            if "handleConversion" not in tag:
                line = content[:match.start()].count("\n") + 1
                results["untracked_ctas"].append({
                    "element": "link",
                    "file": rel_path,
                    "line": line,
                    "snippet": tag[:100],
                })

    # Check for duplicate labels
    for label, count in label_counter.items():
        if count > 1:
            results["duplicate_labels"].append({
                "label": label,
                "count": count,
                "note": "OK if same CTA appears in multiple viewport variants (desktop/mobile)",
            })

    return results


def validate_label_convention(label: str) -> bool:
    """Check if label follows naming convention: 'Section CTA Type'."""
    # Labels should be Title Case and descriptive
    return bool(re.match(r"^[A-Z][a-zA-Záéíóú\s]+$", label))


def main():
    print("=" * 60)
    print("🔍 TRACKING VALIDATOR — CTA Integrity Check")
    print("=" * 60)

    results = scan_ctas()

    # Report tracked CTAs
    print(f"\n✅ Tracked CTAs: {len(results['tracked_ctas'])}")
    for cta in results["tracked_ctas"]:
        convention_ok = "✓" if validate_label_convention(cta["label"]) else "⚠"
        print(f"   {convention_ok} [{cta['label']}] → {cta['file']}:{cta['line']}")

    # Report untracked CTAs
    if results["untracked_ctas"]:
        print(f"\n⚠️  Untracked CTAs (potential signal loss): {len(results['untracked_ctas'])}")
        for cta in results["untracked_ctas"]:
            print(f"   ❌ <{cta['element']}> in {cta['file']}:{cta['line']}")
            print(f"      {cta['snippet']}")
    else:
        print("\n✅ No untracked CTAs found — 100% coverage")

    # Report duplicate labels
    if results["duplicate_labels"]:
        print(f"\nℹ️  Duplicate labels: {len(results['duplicate_labels'])}")
        for dup in results["duplicate_labels"]:
            print(f"   '{dup['label']}' appears {dup['count']}x — {dup['note']}")

    # Summary
    total_tracked = len(results["tracked_ctas"])
    total_untracked = len(results["untracked_ctas"])
    coverage = (total_tracked / (total_tracked + total_untracked) * 100) if (total_tracked + total_untracked) > 0 else 0

    print(f"\n{'=' * 60}")
    print(f"📊 TRACKING COVERAGE: {coverage:.1f}%")
    print(f"   Tracked: {total_tracked} | Untracked: {total_untracked}")

    if total_untracked > 0:
        print(f"\n⚠️  Signal loss risk: {total_untracked} CTAs missing tracking")
        sys.exit(1)
    else:
        print(f"\n✅ All CTAs are tracked — zero signal loss")
        sys.exit(0)


if __name__ == "__main__":
    main()
