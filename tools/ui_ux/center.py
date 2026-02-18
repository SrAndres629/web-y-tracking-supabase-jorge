#!/usr/bin/env python3
"""
🎨 UI/UX Utils: Center Element
==============================
Generates or applies precise CSS/Tailwind for centering elements.
Usage:
    python3 tools/ui_ux/center.py --mode flex --target ".my-div"
"""

import sys
import argparse

def get_centering_css(mode="flex"):
    if mode == "flex":
        return """
display: flex;
justify-content: center;
align-items: center;
"""
    elif mode == "grid":
        return """
display: grid;
place-items: center;
"""
    elif mode == "absolute":
        return """
position: absolute;
top: 50%;
left: 50%;
transform: translate(-50%, -50%);
"""
    return ""

def main():
    parser = argparse.ArgumentParser(description="Center elements with mathematical precision.")
    parser.add_argument("--mode", choices=["flex", "grid", "absolute"], default="flex")
    args = parser.parse_args()

    print(f"/* Centering utilizing {args.mode} */")
    print(get_centering_css(args.mode))

if __name__ == "__main__":
    main()
