## 2026-02-25 - Icon-only Accessibility
**Learning:** Icon-only elements like social links and mobile menu buttons frequently lack `aria-label` attributes on the parent tags and `aria-hidden="true"` on the inner icon elements, which harms accessibility.
**Action:** Always verify that icon-only buttons or links have a descriptive `aria-label` and that the decorative icon itself is hidden from screen readers using `aria-hidden="true"`.
