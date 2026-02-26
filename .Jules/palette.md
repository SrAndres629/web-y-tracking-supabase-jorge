## 2026-02-26 - Icon-Only Buttons and Links
**Learning:** Icon-only buttons (like the mobile menu close button) and links (like social media icons in the footer) are invisible to screen readers without `aria-label`. Visually they are clear, but programmatically they are empty.
**Action:** Always verify that elements containing only `<i>` or `<svg>` tags have an explicit `aria-label` or `aria-labelledby` attribute describing the action or destination.
