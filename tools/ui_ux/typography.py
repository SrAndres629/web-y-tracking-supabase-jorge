#!/usr/bin/env python3
"""
Aa UI/UX Utils: Typography Scale
================================
Returns a mathematical typography scale.
"""

def get_type_scale(base_size=16, ratio=1.25):
    scales = {}
    labels = ["sm", "base", "lg", "xl", "2xl", "3xl", "4xl", "5xl"]

    current = base_size / (ratio ** 2) # Start from small

    css = ":root {\n"
    for label in ["xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl", "5xl"]:
        rem = current / 16
        css += f"  --text-{label}: {rem:.3f}rem; /* {current:.1f}px */\n"
        current *= ratio
    css += "}"
    return css

if __name__ == "__main__":
    print(get_type_scale())
