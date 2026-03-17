
## 2025-02-09 - Accessible Icon-Only Elements
**Learning:** Icon-only elements require an `aria-label` for screen reader accessibility, and the inner icon must have `aria-hidden="true"` to avoid redundant or confusing readout.
**Action:** Always apply `aria-label` on wrapper links/buttons and `aria-hidden="true"` on their child icons.
