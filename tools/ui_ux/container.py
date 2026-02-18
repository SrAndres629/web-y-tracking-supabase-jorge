#!/usr/bin/env python3
"""
📦 UI/UX Utils: Standard Container
==================================
Returns standard container CSS based on breakpoints.
"""

def get_container_css():
    return """
/* Mobile First Container */
width: 100%;
padding-left: 1rem;
padding-right: 1rem;
margin-left: auto;
margin-right: auto;

/* Breakpoints */
@media (min-width: 640px) { max-width: 640px; }
@media (min-width: 768px) { max-width: 768px; }
@media (min-width: 1024px) { max-width: 1024px; }
@media (min-width: 1280px) { max-width: 1280px; }
@media (min-width: 1536px) { max-width: 1536px; }
"""

if __name__ == "__main__":
    print(get_container_css())
