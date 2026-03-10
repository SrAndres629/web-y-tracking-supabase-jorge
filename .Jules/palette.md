## 2024-01-01 - [Init]
**Learning:** Initialize Palette Journal
**Action:** none

## 2026-03-10 - Accessible Icon-Only Elements
**Learning:** Icon-only elements (like social links in footer and mobile menu buttons) need explicit `aria-label` attributes on the parent interactive tag and `aria-hidden="true"` on the inner visual element (e.g., `<i>` or `<span>`). This prevents screen readers from making redundant or confusing announcements while ensuring the element's purpose is clear.
**Action:** Always verify that buttons or links containing only an icon or an HTML entity (like `&times;`) have an accessible name via `aria-label` and hide the inner icon from assistive technologies.
