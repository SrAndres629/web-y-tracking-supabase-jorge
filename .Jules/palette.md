## 2025-03-11 - Accessibility for Icon-only Elements
**Learning:** Icon-only elements such as social links and mobile menu buttons require an `aria-label` attribute on the parent tag to provide context to screen readers, and an `aria-hidden="true"` on the inner icon (e.g., FontAwesome `<i>`) to prevent redundant or confusing readout.
**Action:** Always apply this combination (`aria-label` on wrapper, `aria-hidden="true"` on inner icon) to any interactive element that relies solely on a visual icon.
